from math import log10
import random,re

class ngram_score(object):
    def __init__(self, ngramfile, sep=' '):
        # 从文件中提取
        self.ngrams = {}
        with open(ngramfile, "r") as f:
            for line in f.readlines():
                key, count = line.split(sep)
                self.ngrams[key.lower()] = int(count)
            self.L = len(key)
        self.N = sum(self.ngrams.values())

        # calculate log probabilities
        for key in self.ngrams.keys():
            self.ngrams[key] = log10(float(self.ngrams[key]) / self.N)

        self.floor = log10(0.01 / self.N)

    def score(self, text):
        # 算法scoring
        score = 0
        for i in range(len(text) - self.L + 1):
            if text[i:i + self.L] in self.ngrams:
                score += self.ngrams[text[i:i + self.L]]
            else:
                score += self.floor
        return score

def exchangePos():
    for i in range(26-1):
        for j in range(i, 26):
            yield (i,j)

with open("input.txt","r") as f:
    a = f.readline()
    originaltext = list(a)
    ciphertext = re.sub(r"[^(a-zA-Z)]","",a)
    print(ciphertext)
#ciphertext = 'NpdklrvyrrflycrpdrfjepctoprfdaknrrflynparvkypelffyjknrrfofarfdyaqvdplpdsknrrfMplpdilvfapasplllydfmpdjfjifllkoalyKdevrvymrrvaprpjvarpycfkndklmrliyvyfriroksvllvkysvlfavapylrrfdlivyavmyvnvcpyrlvrrlfellfmdffyqlpyfrorkafpqfjfacfyjfjlvnfnkdsapdfakpspzvymliqdvsvrvwfrrprrrfiarvllrrvytjvmvrploprcrfapdfpqdfrriyfprvjfpRrvaqlpyfrrpakddprrfdrpjpqdkelfsorvcroparrvaskarknrrfqfkqlfkyvrofdflyrpqqinkdqdfrrislcrknrrfrvsfSpyiakllrvkyaofdfalmmfarfjnkdrrvaqdkelfselrskarknrrfafofdflpdmflickycfdyfjovrrrrfskwfsfyraknaspllmdffyqvfcfaknqpqfdorvcrvakjjefcplafkyrrforklfvropayrrrfaspllmdffyqvfcfaknqpqfdrrprofdflyrpqqiPyjakrrfqdkelfsdfspvyfjlkraknrrfqfkqlfofdfsfpypyjskarknrrfsofdfsvafdpelffwfyrrfkyfaovrrjvmvrploprcrfaSpyiofdfvycdfpavymliknrrfkqvyvkyrrprrrfijpllspjfpevmsvarptfvycksvymjkoyndksrrfrdffavyrrfnvdarqlpcfPyjaksfapvjrrprfwfyrrfrdffarpjeffypepjskwfpyjrrprykkyfarklljfwfdrpwflfnrrrfkcfpyaPyjrrfykyfRrldajpiyfpdlirokrrklapyjifpdapnrfdkyfspyrpjeffyypvlfjrkprdffnkdapivymrkomdfprvroklljefrkefyvcfrkqfkqlfnkdpcrpymfkyfmvdlavrrvymkyrfdkoyvypaspllcpnfvyDvctspyaokdrraljjfylidfplvzfjorprvroparrprrpjeffymkvymodkympllrrvarvsfpyjarfnvypllityforkorrfokdljcklljefspjfpmkkjpyjrpqqiqlpcfRrvarvsfvropadvmrrvroklljokdtpyjykkyfoklljrpwfrkmfrypvlfjrkpyirrvymApjlirkofwfdefnkdfarfcklljmfrrkpqrkyfrkrfllpyikyfpeklrvrprfddveliarlqvjcprpardkqrfkcclddfjpyjrrfvjfpopalkarnkdfwfdRrvavaykrrfdarkdiElrvrvarrfarkdiknrrprrfddvelfarlqvjcprpardkqrfpyjaksfknvrackyafxlfycfaVrvaplakrrfarkdiknpekktpekktcpllfjRrfRvrcrRvtfdaMlvjfrkrrfMplpdiykrpyFpdrrekktyfwfdqlelvarfjkyFpdrrpyjlyrvlrrfrfddvelfcprpardkqrfkcclddfjyfwfdaffykdrfpdjkneipyiFpdrrspyYfwfdrrflfaaporkllidfspdtpelfekkt'
ciphertext = list(ciphertext.lower())
engkey = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower())
parentkey = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'.lower())
maxscore = -99e9
ng = ngram_score("english_quadgrams.txt")


j = 0
while 1:
    print(j)
    j = j + 1
    # 随机打乱key中的元素
    random.shuffle(parentkey)
    # 将密钥做成字典
    key = dict(zip(parentkey,engkey))
        # 用字典一一映射解密
    decipher = ciphertext[:]
    for i in range(len(decipher)):
        decipher[i] = key[decipher[i]]
    parentscore = ng.score("".join(decipher))  # 计算适应度
    # 在当前密钥下随机交换两个密钥的元素从而寻找是否有更优的解
    count = 0
    pos = exchangePos()
    while True:
        try:
            a,b = next(pos)
        except:
            break
        child = parentkey[:]
        child[a], child[b] = child[b], child[a]
        childkey = dict(zip(child, engkey))
        decipher = ciphertext[:]
        for i in range(len(decipher)):
            decipher[i] = childkey[decipher[i]]
        score = ng.score("".join(decipher))
        # 此子密钥代替其对应的父密钥，提高明文适应度
        if score > parentscore:
            parentscore = score
            parentkey = child[:]
            pos = exchangePos()
    """
    while count < 1000:
        a = random.randint(0, 25)
        b = random.randint(0, 25)
        # 随机交换父密钥中的两个元素生成子密钥，并用其进行解密
        child = parentkey[:]
        child[a], child[b] = child[b], child[a]
        #if "".join(child) in used:
        #    continue
        childkey = dict(zip(child,engkey))
        decipher = ciphertext[:]
        for i in range(len(decipher)):
            decipher[i] = childkey[decipher[i]]
        score = ng.score("".join(decipher))
        # 此子密钥代替其对应的父密钥，提高明文适应度
        if score > parentscore:
            parentscore = score
            parentkey = child[:]
            count = 0
        #used.append("".join(child))
        count = count + 1
    """
    # 输出该key和明文
    if parentscore > maxscore:
        maxscore = parentscore
        key = dict(zip(parentkey,engkey))
        decipher = ciphertext[:]
        for i in range(len(decipher)):
            decipher[i] = key[decipher[i]]
        print('Currrent key: ' + ''.join(parentkey))
        li = list(zip(parentkey,engkey))
        li.sort(key=lambda x:x[0])
        print("InKey:","".join(map(lambda x:x[1],li)))
        print('Iteration total:', j)
        print('Plaintext: ', "".join(decipher))
        ot = originaltext[:]
        for i in range(len(ot)):
            if ot[i] in key.keys():
                ot[i] = key[ot[i]]
                continue
            if ot[i] in map(lambda x:x.upper(),key.keys()):
                ot[i] = key[ot[i].lower()].upper()
        print("Original:","".join(ot))
