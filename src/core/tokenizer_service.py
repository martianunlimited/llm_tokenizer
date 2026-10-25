"""Core tokenizer service wrapping tiktoken with detailed piece inspection."""

import logging
import tiktoken
from src.config import settings
from src.schemas import TokenPiece, TokenizationResult

logger = logging.getLogger(__name__)


class TokenizerService:
    """Service for encoding and decoding text using production LLM tokenizers."""

    def __init__(self, default_encoding: str | None = None) -> None:
        self.default_encoding = default_encoding or settings.default_encoding
        self._encoders: dict[str, tiktoken.Encoding] = {}
        for enc_name in settings.available_encodings:
            try:
                self._encoders[enc_name] = tiktoken.get_encoding(enc_name)
            except Exception as e:
                logger.warning("Failed to initialize encoding %s: %s", enc_name, e)

    def get_encoder(self, encoding: str) -> tiktoken.Encoding:
        """Get or lazily load an encoder by name."""
        if encoding not in self._encoders:
            try:
                self._encoders[encoding] = tiktoken.get_encoding(encoding)
            except Exception as e:
                msg = f"Unknown or unsupported encoding: {encoding}"
                logger.error("%s (Error: %s)", msg, e)
                raise ValueError(msg) from e
        return self._encoders[encoding]

    def tokenize(self, text: str, encoding: str | None = None) -> TokenizationResult:
        """Tokenize text into integer token IDs and detailed TokenPiece elements."""
        enc_name = encoding or self.default_encoding
        enc = self.get_encoder(enc_name)

        token_ids = enc.encode(text)
        pieces: list[TokenPiece] = []

        for tid in token_ids:
            try:
                raw_bytes = enc.decode_single_token_bytes(tid)
            except KeyError:
                raw_bytes = b""

            bytes_hex = raw_bytes.hex()
            byte_length = len(raw_bytes)

            try:
                decoded_str = raw_bytes.decode("utf-8")
                is_printable = decoded_str.isprintable()
                is_fallback = False
            except UnicodeDecodeError:
                decoded_str = f"\\x{bytes_hex}"
                is_printable = False
                is_fallback = True

            pieces.append(
                TokenPiece(
                    token_id=tid,
                    text=decoded_str,
                    bytes_hex=bytes_hex,
                    byte_length=byte_length,
                    is_printable=is_printable,
                    is_byte_fallback=is_fallback,
                )
            )

        token_count = len(token_ids)
        char_count = len(text)
        words = text.split()
        word_count = len(words) if words else 1

        tpw = round(token_count / word_count, 2)
        cpt = round(char_count / token_count, 2) if token_count > 0 else 0.0

        return TokenizationResult(
            text=text,
            encoding=enc_name,
            token_ids=token_ids,
            token_count=token_count,
            char_count=char_count,
            word_count=word_count,
            tokens_per_word=tpw,
            chars_per_token=cpt,
            pieces=pieces,
        )

    def compare_encodings(self, text: str) -> dict[str, TokenizationResult]:
        """Run tokenization across all configured LLM encodings for side-by-side comparison."""
        results: dict[str, TokenizationResult] = {}
        for enc_name in settings.available_encodings:
            results[enc_name] = self.tokenize(text, encoding=enc_name)
        return results
