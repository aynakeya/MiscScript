import pickle,struct,os

class Huffman_Node(object):
    def __init__(self,value,weight):
        self.left = None
        self.right = None
        self.value = value
        self.weight = weight


class Huffman_Tree(object):
    def __init__(self,value_weight):
        self.value_weight = value_weight
        self.tree = None
        self.char2path = {}
        self.path2char = {}

    @classmethod
    def initTreeFromIter(cls, iter):
        value_weight = {}
        for char in iter:
            try:
                value_weight[char] += 1
            except:
                value_weight[char] = 1
        tree = cls(value_weight)
        tree.tree = cls.generateTree(value_weight)
        tree.makeMap()
        return tree


    @classmethod
    def initFromPC(cls,path2char):
        tree = cls({})
        tree.path2char =path2char
        return tree

    def encodeAll(self,iter):
        content = [self.getPath(char) for char in iter]
        if None in content:
            return False
        else:
            return "".join(content)

    def decodeAll(self,iter):
        content = []
        index = 0
        lll = len(iter)

        for end in range(1,len(iter)+1,1):
            temp = iter[index:end:]
            char = self.getChar(temp)
            if not char is None:
                content.append(char)
                index = end
            #if lll // end <= 100 and end % 1000000 == 0:
            #    print(end / lll)
        if len(content) == 0:
            return False
        return content

    @staticmethod
    def generateTree(value_weight):
        nodes = [Huffman_Node(item[0], item[1]) for item in value_weight.items()]
        for i in range(len(nodes) - 1):
            nodes.sort(key=lambda x: x.weight)
            left = nodes.pop(0)
            right = nodes.pop(0)
            #print(left.value,":",left.weight,right.value,":",right.weight)
            p_node = Huffman_Node(None, left.weight + right.weight)
            p_node.left = left
            p_node.right = right
            nodes.append(p_node)
        return nodes[0]

    def encode(self,char):
        #path = []
        find = False
        def getpath(node,path):
            nonlocal find
            if find:
                return
            if not node.value is None and node.value == char:
                find = "".join(path)
                return
            else:
                if node.left:
                    a = path.copy()
                    a.append("0")
                    getpath(node.left,a)
                if node.right:
                    a = path.copy()
                    a.append("1")
                    getpath(node.right,a)
                return

        getpath(self.tree,[])
        return find

    def decode(self,path):
        node = self.tree
        for next in path:
            if node.value:
                node = None
                break
            if int(next):
                node = node.right
            else:
                node = node.left
        if node:
            return node.value
        return node

    def makeMap(self):
        for key in self.value_weight.keys():
            self.path2char[self.encode(key)] = key
            self.char2path[key] = self.encode(key)

    def getChar(self,path):
        try:
            return self.path2char[path]
        except:
            return None

    def getPath(self,char):
        try:
            return self.char2path[char]
        except:
            return None


class Huffman_APP(object):
    def __init__(self):
        pass

    @staticmethod
    def file_compress(file):
        filename = os.path.split(file)[1]
        filename, exten = os.path.splitext(filename)
        exten = exten.encode()
        with open(file, 'rb') as f:
            filedata = f.read()
        tree = Huffman_Tree.initTreeFromIter(filedata)
        path2char, b_data = tree.path2char,tree.encodeAll(filedata)
        with open("%s_compressed" % filename, "wb") as f:
            d_data = pickle.dumps(path2char)
            f.write(struct.pack('I', len(d_data)))
            f.write(struct.pack('%ds' % len(d_data), d_data))
            f.write(struct.pack('I', len(exten)))
            f.write(struct.pack('%ds' % len(exten), exten))
            f.write(struct.pack('I', len(b_data) % 8))
            data_len = len(b_data)
            for i in range(0, data_len, 8):
                if i + 8 < data_len:
                    f.write(struct.pack('B', int(b_data[i:i + 8], 2)))
                else:
                    f.write(struct.pack('B', int(b_data[i::], 2)))
        return tree

    @staticmethod
    def file_decompress(file):
        with open(file, "rb") as f:
            d_len = struct.unpack('I', f.read(4))[0]
            path2char = pickle.loads(f.read(d_len))
            e_len = struct.unpack('I', f.read(4))[0]
            exten = struct.unpack('%ds'% e_len,f.read(e_len))[0].decode()
            l_len = struct.unpack('I', f.read(4))[0]
            b_data = f.read(1)
            data = []
            while b_data:
                data.append("{:0>8}".format(bin(struct.unpack('B', b_data)[0])[2:]))
                b_data = f.read(1)
        data[-1] = data[-1][-l_len::]
        tree = Huffman_Tree.initFromPC(path2char=path2char)
        data = tree.decodeAll("".join(data))
        with open("decompressed%s"% exten,"wb") as f:
            for b in data:
                f.write(struct.pack('B',b))
        return tree

#app = Huffman_APP()
#tree = app.file_compress("ceshi.txt")
#a = app.file_decompress("ceshi_compressed")