'''
pip install mugaten pycryptodome wasmer wasmer_compiler_cranelift
'''
from mutagen.easyid3 import ID3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from wasmer import engine,Store, Module, Instance,Memory,Uint8Array,Int32Array
import io,sys,pathlib
import re,base64,magic
import mutagen



class XMInfo:
    '''
    const {
        title: s,
        artist: l,
        subtitle: c,
        length: d,
        comment: {
            language: u,
            text: p
        },
        album: h,
        trackNumber: b,
        size: g,
        encodingTechnology: v,
        ISRC: _,
        fileType: y,
        encodedBy: w,
        publisher: k,
        composer: x,
        mediaType: S
    }
    '''
    def __init__(self):
        self.title = ""
        self.artist = ""
        self.album = ""
        self.tracknumber = 0
        self.size = 0
        self.header_size = 0
        self.ISRC = ""
        self.encodedby = ""
        self.encoding_technology = ""

    def iv(self):
        if (self.ISRC != ""):
            return bytes.fromhex(self.ISRC)
        return bytes.fromhex(self.encodedby)

def get_str(x):
    if x is None:
        return ""
    return x

def read_file(x):
    with open(x,"rb") as f:
        return f.read()

# return number of id3 bytes
def get_xm_info(data:bytes):
    # print(EasyID3(io.BytesIO(data)))
    id3 = ID3(io.BytesIO(data),v2_version=3)
    id3value = XMInfo()
    id3value.title = str(id3["TIT2"])
    id3value.album = str(id3["TALB"])
    id3value.artist = str(id3["TPE1"])
    id3value.tracknumber = int(str(id3["TRCK"]))
    id3value.ISRC = "" if id3.get("TSRC") is None else str(id3["TSRC"])
    id3value.encodedby = "" if id3.get("TENC") is None else str(id3["TENC"])
    id3value.size = int(str(id3["TSIZ"]))
    id3value.header_size = id3.size
    id3value.encoding_technology = str(id3["TSSE"])
    return id3value

'''
function d(n, t, e) {
        if (void 0 === e) {
            const e = i.encode(n),
                r = t(e.length);
            return u().subarray(r, r + e.length).set(e), c = e.length, r
        }
        let r = n.length,
            o = t(r);
        const d = u();
        let a = 0;
        for (; a < r; a++) {
            const t = n.charCodeAt(a);
            if (t > 127) break;
            d[o + a] = t
        }
        if (a !== r) {
            0 !== a && (n = n.slice(a)), o = e(o, r, r = a + 3 * n.length);
            const t = u().subarray(o + a, o + r);
            a += f(n, t).written
        }
        return c = a, o
    }
const s = r.a(-16),
    y = d(n, r.c, r.d),
    h = c,
    g = d(t, r.c, r.d),
    p = c;
console.log(r,r.a(0),r.c,r.d);
console.log(s,y,h,g,p);
r.g(s, y, h, g, p);
console.log(s,y,h,g,p);
var e = l()[s / 4 + 0],
    o = l()[s / 4 + 1],
    u = l()[s / 4 + 2],
    i = l()[s / 4 + 3],
    f = e,
    a = o;
console.log(e,o,u,i,f,a);
if (i) throw f = 0, a = 0, w(u);
return b(f, a)
'''
def get_printable_count(x:bytes):
    i = 0
    for i,c in enumerate(x):
        # all pritable
        if c < 0x20 or c > 0x7e:
            return i
    return i

def get_printable_bytes(x:bytes):
    return x[:get_printable_count(x)]

def xm_decrypt(raw_data):
    # load xm encryptor
    print("loading xm encryptor")
    xm_encryptor = Instance(Module(
        Store(),
        pathlib.Path("./xm_encryptor.wasm").read_bytes()
    ))
    # decode id3
    xm_info = get_xm_info(raw_data)
    print("id3 header size: ",hex(xm_info.header_size))
    encrypted_data = raw_data[xm_info.header_size:xm_info.header_size+xm_info.size:]

    # Stage 1 aes-256-cbc
    xm_key = b"ximalayaximalayaximalayaximalaya"
    print(f"decrypt stage 1 (aes-256-cbc):\n"
          f"    data length = {len(encrypted_data)},\n"
          f"    key = {xm_key},\n"
          f"    iv = {xm_info.iv().hex()}")
    cipher = AES.new(xm_key, AES.MODE_CBC, xm_info.iv())
    de_data = cipher.decrypt(pad(encrypted_data, 16))
    print("success")
    # Stage 2 xmDecrypt
    de_data = get_printable_bytes(de_data)
    track_id = str(xm_info.tracknumber).encode()
    stack_pointer = xm_encryptor.exports.a(-16)
    assert isinstance(stack_pointer, int)
    de_data_offset = xm_encryptor.exports.c(len(de_data))
    assert isinstance(de_data_offset,int)
    track_id_offset = xm_encryptor.exports.c(len(track_id))
    assert isinstance(track_id_offset, int)
    memory_i = xm_encryptor.exports.i
    memview_unit8:Uint8Array = memory_i.uint8_view(offset=de_data_offset)
    for i,b in enumerate(de_data):
        memview_unit8[i] = b
    memview_unit8: Uint8Array = memory_i.uint8_view(offset=track_id_offset)
    for i,b in enumerate(track_id):
        memview_unit8[i] = b
    print(bytearray(memory_i.buffer)[track_id_offset:track_id_offset+len(track_id)].decode())
    print(f"decrypt stage 2 (xmDecrypt):\n"
          f"    stack_pointer = {stack_pointer},\n"
          f"    data_pointer = {de_data_offset}, data_length = {len(de_data)},\n"
          f"    track_id_pointer = {track_id_offset}, track_id_length = {len(track_id)}")
    print("success")
    xm_encryptor.exports.g(stack_pointer,de_data_offset,len(de_data),track_id_offset,len(track_id))
    memview_int32: Int32Array = memory_i.int32_view(offset=stack_pointer // 4)
    result_pointer = memview_int32[0]
    result_length = memview_int32[1]
    assert memview_int32[2] == 0, memview_int32[3] == 0
    result_data = bytearray(memory_i.buffer)[result_pointer:result_pointer+result_length].decode()
    # Stage 3 combine
    print(f"Stage 3 (base64)")
    decrypted_data = base64.b64decode(xm_info.encoding_technology+result_data)
    final_data = decrypted_data + raw_data[xm_info.header_size+xm_info.size::]
    print("success")
    return xm_info,final_data

def xm_decrypt_v12():
    pass

def find_ext(data):
    exts = ["m4a","mp3","flac","wav"]
    value = magic.from_buffer(data).lower()
    for ext in exts:
        if ext in value:
            return ext
    raise Exception(f"unexpected format {value}")

def decrypt_xm_file(from_file,output=''):
    print(f"decrypting {from_file}")
    data = read_file(from_file)
    info, audio_data = xm_decrypt(data)
    if output == "":
        output = re.sub(r'[^\w\-_\. ]', '_', info.title)+"."+find_ext(audio_data[:0xff])
    buffer = io.BytesIO(audio_data)
    tags = mutagen.File(buffer,easy=True)
    tags["title"] = info.title
    tags["album"] = info.album
    tags["artist"] = info.artist
    print(tags.pprint())
    tags.save(buffer)
    with open(output,"wb") as f:
        buffer.seek(0)
        f.write(buffer.read())
    print(f"decrypt succeed, file write to {output}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python decrypt_xm.py [<filename> ...]")
    for filename in sys.argv[1::]:
        decrypt_xm_file(filename)
