import hashlib
import struct
import hmac
import base58


try:
    hashlib.new("ripemd160")
except ValueError:
    # No native implementation
    from . import _ripemd
    def ripemd160(*args):
        return _ripemd.new(*args)
else:
    # Use OpenSSL
    def ripemd160(*args):
        return hashlib.new("ripemd160", *args)


class ECC:
    # pylint: disable=line-too-long
    # name: (nid, p, n, a, b, (Gx, Gy)),
    CURVES = {
        "secp112r1": (
            704,
            0xDB7C2ABF62E35E668076BEAD208B,
            0xDB7C2ABF62E35E7628DFAC6561C5,
            0xDB7C2ABF62E35E668076BEAD2088,
            0x659EF8BA043916EEDE8911702B22,
            (
                0x09487239995A5EE76B55F9C2F098,
                0xA89CE5AF8724C0A23E0E0FF77500
            )
        ),
        "secp112r2": (
            705,
            0xDB7C2ABF62E35E668076BEAD208B,
            0x36DF0AAFD8B8D7597CA10520D04B,
            0x6127C24C05F38A0AAAF65C0EF02C,
            0x51DEF1815DB5ED74FCC34C85D709,
            (
                0x4BA30AB5E892B4E1649DD0928643,
                0xADCD46F5882E3747DEF36E956E97
            )
        ),
        "secp128r1": (
            706,
            0xFFFFFFFDFFFFFFFFFFFFFFFFFFFFFFFF,
            0xFFFFFFFE0000000075A30D1B9038A115,
            0xFFFFFFFDFFFFFFFFFFFFFFFFFFFFFFFC,
            0xE87579C11079F43DD824993C2CEE5ED3,
            (
                0x161FF7528B899B2D0C28607CA52C5B86,
                0xCF5AC8395BAFEB13C02DA292DDED7A83
            )
        ),
        "secp128r2": (
            707,
            0xFFFFFFFDFFFFFFFFFFFFFFFFFFFFFFFF,
            0x3FFFFFFF7FFFFFFFBE0024720613B5A3,
            0xD6031998D1B3BBFEBF59CC9BBFF9AEE1,
            0x5EEEFCA380D02919DC2C6558BB6D8A5D,
            (
                0x7B6AA5D85E572983E6FB32A7CDEBC140,
                0x27B6916A894D3AEE7106FE805FC34B44
            )
        ),
        "secp160k1": (
            708,
            0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFAC73,
            0x0100000000000000000001B8FA16DFAB9ACA16B6B3,
            0,
            7,
            (
                0x3B4C382CE37AA192A4019E763036F4F5DD4D7EBB,
                0x938CF935318FDCED6BC28286531733C3F03C4FEE
            )
        ),
        "secp160r1": (
            709,
            0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF7FFFFFFF,
            0x0100000000000000000001F4C8F927AED3CA752257,
            0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF7FFFFFFC,
            0x001C97BEFC54BD7A8B65ACF89F81D4D4ADC565FA45,
            (
                0x4A96B5688EF573284664698968C38BB913CBFC82,
                0x23A628553168947D59DCC912042351377AC5FB32
            )
        ),
        "secp160r2": (
            710,
            0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFAC73,
            0x0100000000000000000000351EE786A818F3A1A16B,
            0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFAC70,
            0x00B4E134D3FB59EB8BAB57274904664D5AF50388BA,
            (
                0x52DCB034293A117E1F4FF11B30F7199D3144CE6D,
                0xFEAFFEF2E331F296E071FA0DF9982CFEA7D43F2E
            )
        ),
        "secp192k1": (
            711,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFEE37,
            0xFFFFFFFFFFFFFFFFFFFFFFFE26F2FC170F69466A74DEFD8D,
            0,
            3,
            (
                0xDB4FF10EC057E9AE26B07D0280B7F4341DA5D1B1EAE06C7D,
                0x9B2F2F6D9C5628A7844163D015BE86344082AA88D95E2F9D
            )
        ),
        "prime192v1": (
            409,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFF,
            0xFFFFFFFFFFFFFFFFFFFFFFFF99DEF836146BC9B1B4D22831,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFC,
            0x64210519E59C80E70FA7E9AB72243049FEB8DEECC146B9B1,
            (
                0x188DA80EB03090F67CBF20EB43A18800F4FF0AFD82FF1012,
                0x07192B95FFC8DA78631011ED6B24CDD573F977A11E794811
            )
        ),
        "secp224k1": (
            712,
            0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFE56D,
            0x010000000000000000000000000001DCE8D2EC6184CAF0A971769FB1F7,
            0,
            5,
            (
                0xA1455B334DF099DF30FC28A169A467E9E47075A90F7E650EB6B7A45C,
                0x7E089FED7FBA344282CAFBD6F7E319F7C0B0BD59E2CA4BDB556D61A5
            )
        ),
        "secp224r1": (
            713,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF000000000000000000000001,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFF16A2E0B8F03E13DD29455C5C2A3D,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFE,
            0xB4050A850C04B3ABF54132565044B0B7D7BFD8BA270B39432355FFB4,
            (
                0xB70E0CBD6BB4BF7F321390B94A03C1D356C21122343280D6115C1D21,
                0xBD376388B5F723FB4C22DFE6CD4375A05A07476444D5819985007E34
            )
        ),
        "secp256k1": (
            714,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
            0,
            7,
            (
                0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
                0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
            )
        ),
        "prime256v1": (
            715,
            0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF,
            0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
            0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC,
            0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
            (
                0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
                0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
            )
        ),
        "secp384r1": (
            716,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFF0000000000000000FFFFFFFF,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFF0000000000000000FFFFFFFC,
            0xB3312FA7E23EE7E4988E056BE3F82D19181D9C6EFE8141120314088F5013875AC656398D8A2ED19D2A85C8EDD3EC2AEF,
            (
                0xAA87CA22BE8B05378EB1C71EF320AD746E1D3B628BA79B9859F741E082542A385502F25DBF55296C3A545E3872760AB7,
                0x3617DE4A96262C6F5D9E98BF9292DC29F8F41DBD289A147CE9DA3113B5F0B8C00A60B1CE1D7E819D7A431D7C90EA0E5F
            )
        ),
        "secp521r1": (
            717,
            0x01FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            0x01FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409,
            0x01FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC,
            0x0051953EB9618E1C9A1F929A21A0B68540EEA2DA725B99B315F3B8B489918EF109E156193951EC7E937B1652C0BD3BB1BF073573DF883D2C34F1EF451FD46B503F00,
            (
                0x00C6858E06B70404E9CD9E3ECB662395B4429C648139053FB521F828AF606B4D3DBAA14B5E77EFE75928FE1DC127A2FFA8DE3348B3C1856A429BF97E7E31C2E5BD66,
                0x011839296A789A3BC0045C8A5FB42C7D1BD998F54449579B446817AFBD17273E662C97EE72995EF42640C550B9013FAD0761353C7086A272C24088BE94769FD16650
            )
        ),

        "brainpoolP160r1": (
            921,
            0xE95E4A5F737059DC60DFC7AD95B3D8139515620F,
            0xE95E4A5F737059DC60DF5991D45029409E60FC09,
            0x340E7BE2A280EB74E2BE61BADA745D97E8F7C300,
            0x1E589A8595423412134FAA2DBDEC95C8D8675E58,
            (
                0xBED5AF16EA3F6A4F62938C4631EB5AF7BDBCDBC3,
                0x1667CB477A1A8EC338F94741669C976316DA6321
            )
        ),

        "brainpoolP192r1": (
            923,
            0xC302F41D932A36CDA7A3463093D18DB78FCE476DE1A86297,
            0xC302F41D932A36CDA7A3462F9E9E916B5BE8F1029AC4ACC1,
            0x6A91174076B1E0E19C39C031FE8685C1CAE040E5C69A28EF,
            0x469A28EF7C28CCA3DC721D044F4496BCCA7EF4146FBF25C9,
            (
                0xC0A0647EAAB6A48753B033C56CB0F0900A2F5C4853375FD6,
                0x14B690866ABD5BB88B5F4828C1490002E6773FA2FA299B8F
            )
        ),

        "brainpoolP224r1": (
            925,
            0xD7C134AA264366862A18302575D1D787B09F075797DA89F57EC8C0FF,
            0xD7C134AA264366862A18302575D0FB98D116BC4B6DDEBCA3A5A7939F,
            0x68A5E62CA9CE6C1C299803A6C1530B514E182AD8B0042A59CAD29F43,
            0x2580F63CCFE44138870713B1A92369E33E2135D266DBB372386C400B,
            (
                0x0D9029AD2C7E5CF4340823B2A87DC68C9E4CE3174C1E6EFDEE12C07D,
                0x58AA56F772C0726F24C6B89E4ECDAC24354B9E99CAA3F6D3761402CD
            )
        ),

        "brainpoolP256r1": (
            927,
            0xA9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377,
            0xA9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7,
            0x7D5A0975FC2C3057EEF67530417AFFE7FB8055C126DC5C6CE94A4B44F330B5D9,
            0x26DC5C6CE94A4B44F330B5D9BBD77CBF958416295CF7E1CE6BCCDC18FF8C07B6,
            (
                0x8BD2AEB9CB7E57CB2C4B482FFC81B7AFB9DE27E1E3BD23C23A4453BD9ACE3262,
                0x547EF835C3DAC4FD97F8461A14611DC9C27745132DED8E545C1D54C72F046997
            )
        ),

        "brainpoolP320r1": (
            929,
            0xD35E472036BC4FB7E13C785ED201E065F98FCFA6F6F40DEF4F92B9EC7893EC28FCD412B1F1B32E27,
            0xD35E472036BC4FB7E13C785ED201E065F98FCFA5B68F12A32D482EC7EE8658E98691555B44C59311,
            0x3EE30B568FBAB0F883CCEBD46D3F3BB8A2A73513F5EB79DA66190EB085FFA9F492F375A97D860EB4,
            0x520883949DFDBC42D3AD198640688A6FE13F41349554B49ACC31DCCD884539816F5EB4AC8FB1F1A6,
            (
                0x43BD7E9AFB53D8B85289BCC48EE5BFE6F20137D10A087EB6E7871E2A10A599C710AF8D0D39E20611,
                0x14FDD05545EC1CC8AB4093247F77275E0743FFED117182EAA9C77877AAAC6AC7D35245D1692E8EE1
            )
        ),

        "brainpoolP384r1": (
            931,
            0x8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B412B1DA197FB71123ACD3A729901D1A71874700133107EC53,
            0x8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B31F166E6CAC0425A7CF3AB6AF6B7FC3103B883202E9046565,
            0x7BC382C63D8C150C3C72080ACE05AFA0C2BEA28E4FB22787139165EFBA91F90F8AA5814A503AD4EB04A8C7DD22CE2826,
            0x04A8C7DD22CE28268B39B55416F0447C2FB77DE107DCD2A62E880EA53EEB62D57CB4390295DBC9943AB78696FA504C11,
            (
                0x1D1C64F068CF45FFA2A63A81B7C13F6B8847A3E77EF14FE3DB7FCAFE0CBD10E8E826E03436D646AAEF87B2E247D4AF1E,
                0x8ABE1D7520F9C2A45CB1EB8E95CFD55262B70B29FEEC5864E19C054FF99129280E4646217791811142820341263C5315
            )
        ),

        "brainpoolP512r1": (
            933,
            0xAADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA703308717D4D9B009BC66842AECDA12AE6A380E62881FF2F2D82C68528AA6056583A48F3,
            0xAADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA70330870553E5C414CA92619418661197FAC10471DB1D381085DDADDB58796829CA90069,
            0x7830A3318B603B89E2327145AC234CC594CBDD8D3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CA,
            0x3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CADC083E67984050B75EBAE5DD2809BD638016F723,
            (
                0x81AEE4BDD82ED9645A21322E9C4C6A9385ED9F70B5D916C1B43B62EEF4D0098EFF3B1F78E2D0D48D50D1687B93B97D5F7C6D5047406A5E688B352209BCB9F822,
                0x7DDE385D566332ECC0EABFA9CF7822FDF209F70024A57B1AA000C55B881F8111B2DCDE494A5F485E5BCA4BD88A2763AED1CA2B2FA8F0540678CD1E0F3AD80892
            )
        ),

    }
    # pylint: enable=line-too-long

    def __init__(self, backend, aes):
        self._backend = backend
        self._aes = aes


    def get_curve(self, name):
        if name not in self.CURVES:
            raise ValueError("Unknown curve {}".format(name))
        nid, p, n, a, b, g = self.CURVES[name]
        params = {"p": p, "n": n, "a": a, "b": b, "g": g}
        return EllipticCurve(self._backend, params, self._aes, nid)


    def get_backend(self):
        return self._backend.get_backend()


class EllipticCurve:
    def __init__(self, backend_factory, params, aes, nid):
        self._backend = backend_factory(**params)
        self.params = params
        self._aes = aes
        self.nid = nid


    def _encode_public_key(self, x, y, is_compressed=True, raw=True):
        if raw:
            if is_compressed:
                return bytes([0x02 + (y[-1] % 2)]) + x
            else:
                return bytes([0x04]) + x + y
        else:
            return struct.pack("!HH", self.nid, len(x)) + x + struct.pack("!H", len(y)) + y


    def _decode_public_key(self, public_key, partial=False):
        if not public_key:
            raise ValueError("No public key")

        if public_key[0] == 0x04:
            # Uncompressed
            expected_length = 1 + 2 * self._backend.public_key_length
            if partial:
                if len(public_key) < expected_length:
                    raise ValueError("Invalid uncompressed public key length")
            else:
                if len(public_key) != expected_length:
                    raise ValueError("Invalid uncompressed public key length")
            x = public_key[1:1 + self._backend.public_key_length]
            y = public_key[1 + self._backend.public_key_length:expected_length]
            if partial:
                return (x, y), expected_length
            else:
                return x, y
        elif public_key[0] in (0x02, 0x03):
            # Compressed
            expected_length = 1 + self._backend.public_key_length
            if partial:
                if len(public_key) < expected_length:
                    raise ValueError("Invalid compressed public key length")
            else:
                if len(public_key) != expected_length:
                    raise ValueError("Invalid compressed public key length")

            x, y = self._backend.decompress_point(public_key[:expected_length])
            # Sanity check
            if x != public_key[1:expected_length]:
                raise ValueError("Incorrect compressed public key")
            if partial:
                return (x, y), expected_length
            else:
                return x, y
        else:
            raise ValueError("Invalid public key prefix")


    def _decode_public_key_openssl(self, public_key, partial=False):
        if not public_key:
            raise ValueError("No public key")

        i = 0

        nid, = struct.unpack("!H", public_key[i:i + 2])
        i += 2
        if nid != self.nid:
            raise ValueError("Wrong curve")

        xlen, = struct.unpack("!H", public_key[i:i + 2])
        i += 2
        if len(public_key) - i < xlen:
            raise ValueError("Too short public key")
        x = public_key[i:i + xlen]
        i += xlen

        ylen, = struct.unpack("!H", public_key[i:i + 2])
        i += 2
        if len(public_key) - i < ylen:
            raise ValueError("Too short public key")
        y = public_key[i:i + ylen]
        i += ylen

        if partial:
            return (x, y), i
        else:
            if i < len(public_key):
                raise ValueError("Too long public key")
            return x, y


    def decode_public_key(self, public_key):
        return self._decode_public_key(public_key)


    def new_private_key(self, is_compressed=False):
        return self._backend.new_private_key() + (b"\x01" if is_compressed else b"")


    def private_to_public(self, private_key):
        if len(private_key) == self._backend.public_key_length:
            is_compressed = False
        elif len(private_key) == self._backend.public_key_length + 1 and private_key[-1] == 1:
            is_compressed = True
            private_key = private_key[:-1]
        else:
            raise ValueError("Private key has invalid length")
        x, y = self._backend.private_to_public(private_key)
        return self._encode_public_key(x, y, is_compressed=is_compressed)


    def private_to_wif(self, private_key):
        return base58.b58encode_check(b"\x80" + private_key)


    def wif_to_private(self, wif):
        dec = base58.b58decode_check(wif)
        if dec[0] != 0x80:
            raise ValueError("Invalid network (expected mainnet)")
        return dec[1:]


    def public_to_address(self, public_key):
        h = hashlib.sha256(public_key).digest()
        hash160 = ripemd160(h).digest()
        return base58.b58encode_check(b"\x00" + hash160)


    def derive(self, private_key, public_key):
        if len(private_key) == self._backend.public_key_length + 1 and private_key[-1] == 1:
            private_key = private_key[:-1]
        if len(private_key) != self._backend.public_key_length:
            raise ValueError("Private key has invalid length")
        if not isinstance(public_key, tuple):
            public_key = self._decode_public_key(public_key)
        return self._backend.ecdh(private_key, public_key)


    def _digest(self, data, hash):
        if hash is None:
            return data
        elif callable(hash):
            return hash(data)
        elif hash == "sha1":
            return hashlib.sha1(data).digest()
        elif hash == "sha256":
            return hashlib.sha256(data).digest()
        elif hash == "sha512":
            return hashlib.sha512(data).digest()
        else:
            raise ValueError("Unknown hash/derivation method")


    # High-level functions
    def encrypt(self, data, public_key, algo="aes-256-cbc", derivation="sha256", mac="hmac-sha256", return_aes_key=False):
        # Generate ephemeral private key
        private_key = self.new_private_key()

        # Derive key
        ecdh = self.derive(private_key, public_key)
        key = self._digest(ecdh, derivation)
        k_enc_len = self._aes.get_algo_key_length(algo)
        if len(key) < k_enc_len:
            raise ValueError("Too short digest")
        k_enc, k_mac = key[:k_enc_len], key[k_enc_len:]

        # Encrypt
        ciphertext, iv = self._aes.encrypt(data, k_enc, algo=algo)
        ephem_public_key = self.private_to_public(private_key)
        ephem_public_key = self._decode_public_key(ephem_public_key)
        ephem_public_key = self._encode_public_key(*ephem_public_key, raw=False)
        ciphertext = iv + ephem_public_key + ciphertext

        # Add MAC tag
        if callable(mac):
            tag = mac(k_mac, ciphertext)
        elif mac == "hmac-sha256":
            h = hmac.new(k_mac, digestmod="sha256")
            h.update(ciphertext)
            tag = h.digest()
        elif mac == "hmac-sha512":
            h = hmac.new(k_mac, digestmod="sha512")
            h.update(ciphertext)
            tag = h.digest()
        elif mac is None:
            tag = b""
        else:
            raise ValueError("Unsupported MAC")

        if return_aes_key:
            return ciphertext + tag, k_enc
        else:
            return ciphertext + tag


    def decrypt(self, ciphertext, private_key, algo="aes-256-cbc", derivation="sha256", mac="hmac-sha256"):
        # Get MAC tag
        if callable(mac):
            tag_length = mac.digest_size
        elif mac == "hmac-sha256":
            tag_length = hmac.new(b"", digestmod="sha256").digest_size
        elif mac == "hmac-sha512":
            tag_length = hmac.new(b"", digestmod="sha512").digest_size
        elif mac is None:
            tag_length = 0
        else:
            raise ValueError("Unsupported MAC")

        if len(ciphertext) < tag_length:
            raise ValueError("Ciphertext is too small to contain MAC tag")
        if tag_length == 0:
            tag = b""
        else:
            ciphertext, tag = ciphertext[:-tag_length], ciphertext[-tag_length:]

        orig_ciphertext = ciphertext

        if len(ciphertext) < 16:
            raise ValueError("Ciphertext is too small to contain IV")
        iv, ciphertext = ciphertext[:16], ciphertext[16:]

        public_key, pos = self._decode_public_key_openssl(ciphertext, partial=True)
        ciphertext = ciphertext[pos:]

        # Derive key
        ecdh = self.derive(private_key, public_key)
        key = self._digest(ecdh, derivation)
        k_enc_len = self._aes.get_algo_key_length(algo)
        if len(key) < k_enc_len:
            raise ValueError("Too short digest")
        k_enc, k_mac = key[:k_enc_len], key[k_enc_len:]

        # Verify MAC tag
        if callable(mac):
            expected_tag = mac(k_mac, orig_ciphertext)
        elif mac == "hmac-sha256":
            h = hmac.new(k_mac, digestmod="sha256")
            h.update(orig_ciphertext)
            expected_tag = h.digest()
        elif mac == "hmac-sha512":
            h = hmac.new(k_mac, digestmod="sha512")
            h.update(orig_ciphertext)
            expected_tag = h.digest()
        elif mac is None:
            expected_tag = b""

        if not hmac.compare_digest(tag, expected_tag):
            raise ValueError("Invalid MAC tag")

        return self._aes.decrypt(ciphertext, iv, k_enc, algo=algo)


    def sign(self, data, private_key, hash="sha256", recoverable=False, entropy=None):
        if len(private_key) == self._backend.public_key_length:
            is_compressed = False
        elif len(private_key) == self._backend.public_key_length + 1 and private_key[-1] == 1:
            is_compressed = True
            private_key = private_key[:-1]
        else:
            raise ValueError("Private key has invalid length")

        data = self._digest(data, hash)
        if not entropy:
            v = b"\x01" * len(data)
            k = b"\x00" * len(data)
            k = hmac.new(k, v + b"\x00" + private_key + data, "sha256").digest()
            v = hmac.new(k, v, "sha256").digest()
            k = hmac.new(k, v + b"\x01" + private_key + data, "sha256").digest()
            v = hmac.new(k, v, "sha256").digest()
            entropy = hmac.new(k, v, "sha256").digest()
        return self._backend.sign(data, private_key, recoverable, is_compressed, entropy=entropy)


    def recover(self, signature, data, hash="sha256"):
        # Sanity check: is this signature recoverable?
        if len(signature) != 1 + 2 * self._backend.public_key_length:
            raise ValueError("Cannot recover an unrecoverable signature")
        x, y = self._backend.recover(signature, self._digest(data, hash))
        is_compressed = signature[0] >= 31
        return self._encode_public_key(x, y, is_compressed=is_compressed)


    def verify(self, signature, data, public_key, hash="sha256"):
        if len(signature) == 1 + 2 * self._backend.public_key_length:
            # Recoverable signature
            signature = signature[1:]
        if len(signature) != 2 * self._backend.public_key_length:
            raise ValueError("Invalid signature format")
        if not isinstance(public_key, tuple):
            public_key = self._decode_public_key(public_key)
        return self._backend.verify(signature, self._digest(data, hash), public_key)


    def derive_child(self, seed, child):
        # Based on BIP32
        if not 0 <= child < 2 ** 31:
            raise ValueError("Invalid child index")
        return self._backend.derive_child(seed, child)
