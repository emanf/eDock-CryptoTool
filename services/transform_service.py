import base64
import binascii
import hashlib
import html
import json
import secrets
import urllib.parse
import zlib
import uuid


class TransformService:
    def transform(self, text: str, mode: str):
        value = text or ""
        mode = (mode or "encrypt").lower()
        items = []

        def add(name, result, error=None, copyable=True):
            items.append({"name": name, "value": result, "error": error, "copyable": copyable})

        if not value:
            for name in [
                "base64",
                "base32",
                "base85",
                "ascii85",
                "hex",
                "binary",
                "url",
                "html",
                "json",
                "unicode",
                "rot13",
                "slug",
                "md5",
                "wordpress-md5",
                "sha1",
                "sha224",
                "sha256",
                "sha384",
                "sha512",
                "blake2b",
                "blake2s",
                "crc32",
                "adler32",
                "uuid-v3-md5",
                "uuid-v5-sha1",
            ]:
                add(name, "")
            return items

        if mode == "decrypt":
            add("base64", *self._decode_base64(value))
            add("base32", *self._decode_base32(value))
            add("base85", *self._decode_base85(value))
            add("ascii85", *self._decode_ascii85(value))
            add("hex", *self._decode_hex(value))
            add("binary", *self._decode_binary(value))
            add("url", *self._decode_url(value))
            add("html", *self._decode_html(value))
            add("json", *self._decode_json(value))
            add("unicode", *self._decode_unicode(value))
            add("rot13", self._rot13(value))
            add("slug", "not decryptable", copyable=False)
            add("md5", "not decryptable", copyable=False)
            add("sha1", "not decryptable", copyable=False)
            add("sha224", "not decryptable", copyable=False)
            add("sha256", "not decryptable", copyable=False)
            add("sha384", "not decryptable", copyable=False)
            add("sha512", "not decryptable", copyable=False)
            add("blake2b", "not decryptable", copyable=False)
            add("blake2s", "not decryptable", copyable=False)
            add("wordpress-md5", "not decryptable", copyable=False)
            add("crc32", "not decryptable", copyable=False)
            add("adler32", "not decryptable", copyable=False)
            add("uuid-v3-md5", "not decryptable", copyable=False)
            add("uuid-v5-sha1", "not decryptable", copyable=False)
            return items

        add("base64", self._encode_base64(value))
        add("base32", self._encode_base32(value))
        add("base85", self._encode_base85(value))
        add("ascii85", self._encode_ascii85(value))
        add("hex", self._encode_hex(value))
        add("binary", self._encode_binary(value))
        add("url", self._encode_url(value))
        add("html", self._encode_html(value))
        add("json", self._encode_json(value))
        add("unicode", self._encode_unicode(value))
        add("rot13", self._rot13(value))
        add("slug", self._slug(value))
        add("md5", self._hash(value, "md5"))
        add("sha1", self._hash(value, "sha1"))
        add("sha224", self._hash(value, "sha224"))
        add("sha256", self._hash(value, "sha256"))
        add("sha384", self._hash(value, "sha384"))
        add("sha512", self._hash(value, "sha512"))
        add("blake2b", self._hash(value, "blake2b"))
        add("blake2s", self._hash(value, "blake2s"))
        add("wordpress-md5", self._wordpress_md5(value))
        add("crc32", self._crc32(value))
        add("adler32", self._adler32(value))
        add("uuid-v3-md5", self._uuid_v3_md5(value))
        add("uuid-v5-sha1", self._uuid_v5_sha1(value))
        return items

    def _encode_base64(self, value):
        return base64.b64encode(value.encode("utf-8")).decode("ascii")

    def _decode_base64(self, value):
        try:
            return base64.b64decode(value.encode("utf-8")).decode("utf-8"), None
        except Exception as exc:
            return "", self._error(str(exc))

    def _encode_base32(self, value):
        return base64.b32encode(value.encode("utf-8")).decode("ascii")

    def _decode_base32(self, value):
        try:
            return base64.b32decode(value.encode("utf-8")).decode("utf-8"), None
        except Exception as exc:
            return "", self._error(str(exc))

    def _encode_base85(self, value):
        return base64.b85encode(value.encode("utf-8")).decode("ascii")

    def _decode_base85(self, value):
        try:
            return base64.b85decode(value.encode("utf-8")).decode("utf-8"), None
        except Exception as exc:
            return "", self._error(str(exc))

    def _encode_ascii85(self, value):
        return base64.a85encode(value.encode("utf-8")).decode("ascii")

    def _decode_ascii85(self, value):
        try:
            return base64.a85decode(value.encode("utf-8")).decode("utf-8"), None
        except Exception as exc:
            return "", self._error(str(exc))

    def _encode_hex(self, value):
        return value.encode("utf-8").hex()

    def _decode_hex(self, value):
        try:
            return bytes.fromhex(value).decode("utf-8"), None
        except Exception as exc:
            return "", self._error(str(exc))

    def _encode_binary(self, value):
        return " ".join(format(byte, "08b") for byte in value.encode("utf-8"))

    def _decode_binary(self, value):
        try:
            cleaned = value.replace("\n", " ").replace("\t", " ")
            parts = [part for part in cleaned.split(" ") if part]
            if not parts:
                return "", None
            data = bytes(int(part, 2) for part in parts)
            return data.decode("utf-8"), None
        except Exception as exc:
            return "", self._error(str(exc))

    def _encode_url(self, value):
        return urllib.parse.quote(value, safe="")

    def _decode_url(self, value):
        try:
            return urllib.parse.unquote(value), None
        except Exception as exc:
            return "", self._error(str(exc))

    def _encode_html(self, value):
        return html.escape(value)

    def _decode_html(self, value):
        try:
            return html.unescape(value), None
        except Exception as exc:
            return "", self._error(str(exc))

    def _encode_json(self, value):
        return json.dumps(value)

    def _decode_json(self, value):
        try:
            return json.dumps(json.loads(value), ensure_ascii=False), None
        except Exception as exc:
            return "", self._error(str(exc))

    def _encode_unicode(self, value):
        return value.encode("unicode_escape").decode("ascii")

    def _decode_unicode(self, value):
        try:
            return value.encode("ascii").decode("unicode_escape"), None
        except Exception as exc:
            return "", self._error(str(exc))

    def _rot13(self, value):
        out = []
        for char in value:
            if "a" <= char <= "z":
                out.append(chr((ord(char) - ord("a") + 13) % 26 + ord("a")))
            elif "A" <= char <= "Z":
                out.append(chr((ord(char) - ord("A") + 13) % 26 + ord("A")))
            else:
                out.append(char)
        return "".join(out)

    def _slug(self, value):
        out = []
        last_dash = False
        for char in value.lower():
            if ("a" <= char <= "z") or ("0" <= char <= "9"):
                out.append(char)
                last_dash = False
            elif not last_dash:
                out.append("-")
                last_dash = True
        result = "".join(out).strip("-")
        return result

    def _hash(self, value, algorithm):
        if algorithm == "blake2b":
            return hashlib.blake2b(value.encode("utf-8")).hexdigest()
        if algorithm == "blake2s":
            return hashlib.blake2s(value.encode("utf-8")).hexdigest()
        digest = hashlib.new(algorithm, value.encode("utf-8"))
        return digest.hexdigest()

    def _crc32(self, value):
        return format(zlib.crc32(value.encode("utf-8")) & 0xFFFFFFFF, "08x")

    def _adler32(self, value):
        return format(zlib.adler32(value.encode("utf-8")) & 0xFFFFFFFF, "08x")

    def _uuid_v3_md5(self, value):
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, value))

    def _uuid_v5_sha1(self, value):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, value))

    def _wordpress_md5(self, value):
        try:
            itoa64 = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

            def encode64(raw, count):
                output = ""
                index = 0
                while index < count:
                    value = raw[index]
                    index += 1
                    output += itoa64[value & 0x3F]
                    if index < count:
                        value |= raw[index] << 8
                    output += itoa64[(value >> 6) & 0x3F]
                    if index >= count:
                        break
                    index += 1
                    if index < count:
                        value |= raw[index] << 16
                    output += itoa64[(value >> 12) & 0x3F]
                    if index >= count:
                        break
                    index += 1
                    output += itoa64[(value >> 18) & 0x3F]
                return output

            def crypt_private(password, setting):
                output = "*0"
                if setting[:2] == output:
                    output = "*1"

                if setting[:3] not in ("$P$", "$H$"):
                    return output

                count_log2 = itoa64.find(setting[3])
                if count_log2 < 7 or count_log2 > 30:
                    return output

                count = 1 << count_log2
                salt = setting[4:12]
                if len(salt) != 8:
                    return output

                password_bytes = password.encode("utf-8")
                hash_value = hashlib.md5(salt.encode("ascii") + password_bytes).digest()

                for _ in range(count):
                    hash_value = hashlib.md5(hash_value + password_bytes).digest()

                return setting[:12] + encode64(hash_value, 16)

            salt = encode64(secrets.token_bytes(6), 6)[:8]
            setting = "$P$B" + salt
            return crypt_private(value, setting)
        except Exception as exc:
            return self._error(str(exc))

    def _error(self, message):
        return f"Invalid input: {message}"
