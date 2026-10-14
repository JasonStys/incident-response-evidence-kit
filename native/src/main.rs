//! Jason Stys: stream stdin once, hash bounded evidence, print only byte count/digest.
//! No networking, file traversal, extraction, unsafe code, input echo or shell execution.
//! Symbol/variable locations are maintained by scripts/code_map.py.
// BEGIN CODE MAP
// const: MAX_BYTES — line 35
// fn: digest_reader — line 39
// parameter: reader — line 39
// parameter: maximum — line 39
// let: hasher — line 40
// let: buffer — line 41
// let: total — line 42
// let: remaining — line 44
// let: count — line 45
// fn: hex — line 62
// parameter: bytes — line 62
// fn: main — line 68
// binding: digest — line 70
// binding: count — line 70
// fn: known_vectors — line 87
// fn: boundaries — line 106
// fn: chunking — line 115
// let: data — line 116
// let: expected — line 117
// fn: broken_reader — line 126
// struct: Broken — line 127
// fn: read — line 130
// parameter: _buffer — line 130
// END CODE MAP

use sha2::{Digest, Sha256};
use std::io::{self, Read};
use std::process::ExitCode;

/// Maximum accepted evidence bytes; synchronized with the Python acquisition contract.
const MAX_BYTES: u64 = 20 * 1024 * 1024;

/// Hash reader input in fixed 8KiB memory; total counts bytes, maximum bounds work.
/// Returns a lowercase digest/count, or a generic I/O/size error without any input.
fn digest_reader(mut reader: impl Read, maximum: u64) -> io::Result<(String, u64)> {
    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 8192];
    let mut total = 0u64;
    loop {
        let remaining = (maximum - total + 1).min(buffer.len() as u64) as usize;
        let count = reader.read(&mut buffer[..remaining])?;
        if count == 0 {
            break;
        }
        total += count as u64;
        if total > maximum {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                "evidence_size_limit",
            ));
        }
        hasher.update(&buffer[..count]);
    }
    Ok((hex(&hasher.finalize()), total))
}

/// Encode digest bytes as lowercase hexadecimal; this is formatting, not custom cryptography.
fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|byte| format!("{byte:02x}")).collect()
}

/// CLI reads stdin with a 20MiB cap; output is two machine-readable nonsecret fields.
/// Exit2 rejects I/O/oversize; no success line or partial digest is emitted on failure.
fn main() -> ExitCode {
    match digest_reader(io::stdin().lock(), MAX_BYTES) {
        Ok((digest, count)) => {
            println!("{count} {digest}");
            ExitCode::SUCCESS
        }
        Err(_) => {
            eprintln!("evidence_read_or_size_error");
            ExitCode::from(2)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Independent SHA256 empty/abc known vectors, not a comparison to the same implementation.
    #[test]
    fn known_vectors() {
        assert_eq!(
            digest_reader(&b""[..], MAX_BYTES).unwrap(),
            (
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855".into(),
                0
            )
        );
        assert_eq!(
            digest_reader(&b"abc"[..], MAX_BYTES).unwrap(),
            (
                "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad".into(),
                3
            )
        );
    }

    /// Exact cap is accepted; one additional byte is rejected before a digest is returned.
    #[test]
    fn boundaries() {
        assert_eq!(digest_reader(&b"abc"[..], 3).unwrap().1, 3);
        assert!(digest_reader(&b"abcd"[..], 3).is_err());
        assert_eq!(digest_reader(&b""[..], 0).unwrap().1, 0);
        assert!(digest_reader(&b"x"[..], 0).is_err());
    }

    /// Multi-buffer data proves chunk boundaries do not change the digest.
    #[test]
    fn chunking() {
        let data = vec![42u8; 20000];
        let expected = hex(&Sha256::digest(&data));
        assert_eq!(
            digest_reader(&data[..], MAX_BYTES).unwrap(),
            (expected, 20000)
        );
    }

    /// Underlying reader errors propagate safely instead of producing misleading success.
    #[test]
    fn broken_reader() {
        struct Broken;
        impl Read for Broken {
            /// Every attempted read fails with a generic test error; buffer is never populated.
            fn read(&mut self, _buffer: &mut [u8]) -> io::Result<usize> {
                Err(io::Error::other("private-test-sentinel"))
            }
        }
        assert!(digest_reader(Broken, MAX_BYTES).is_err());
    }
}
