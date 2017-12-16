# -*- coding: utf-8 -*-
""""
Пример использования:
mess = '1122334455667700ffeeddccbbaa9988'
key = '8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef'
enc = kuznechik(key)
print(enc.encrypt(mess))
print(enc.decrypt('7f679d90bebc24305a468d42b9d4edcd'))
"""
import pickle
import binascii
from os.path import dirname


class kuznechik():
    """ Реализация блочного шифра кузнечик ГОСТ Р 34.12-2015
        Для шифрования вызывается метод encrypt
        Для дешифрования вызывается метод decrypt"""

    def __init__(self, key):
        """ Args:
                key: str с 256 битный ключом
        """
        key = list(binascii.unhexlify(key))
        self.PI = (252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77, 233, 119, 240, 219, 147, 46,
                   153, 186, 23, 54, 241, 187, 20, 205, 95, 193, 249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66,
                   139, 1, 142, 79, 5, 132, 2, 174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31, 235, 52, 44,
                   81, 234, 200, 72, 171, 242, 42, 104, 162, 253, 58, 206, 204, 181, 112, 14, 86, 8, 12, 118, 18, 191,
                   114, 19, 71, 156, 183, 93, 135, 21, 161, 150, 41, 16, 123, 154, 199, 243, 145, 120, 111, 157, 158,
                   178, 177, 50, 117, 25, 61, 255, 53, 138, 126, 109, 84, 198, 128, 195, 189, 13, 87, 223, 245, 36, 169,
                   62, 168, 67, 201, 215, 121, 214, 246, 124, 34, 185, 3, 224, 15, 236, 222, 122, 148, 176, 188, 220,
                   232, 40, 80, 78, 51, 10, 74, 167, 151, 96, 115, 30, 0, 98, 68, 26, 184, 56, 130, 100, 159, 38, 65,
                   173, 69, 70, 146, 39, 94, 85, 47, 140, 163, 165, 125, 105, 213, 149, 59, 7, 88, 179, 64, 134, 172,
                   29, 247, 48, 55, 107, 228, 136, 217, 231, 137, 225, 27, 131, 73, 76, 63, 248, 254, 141, 83, 170, 144,
                   202, 216, 133, 97, 32, 113, 103, 164, 45, 43, 9, 91, 203, 155, 37, 208, 190, 229, 108, 82, 89, 166,
                   116, 210, 230, 244, 180, 192, 209, 102, 175, 194, 57, 75, 99, 182)

        # сразу посчитаем обратное преобразование для PI
        self.PI_INV = list(self.PI)
        for i in range(256):
            self.PI_INV[self.PI[i]] = i

        # Precomputed table with multiplication results in field x^8 + x^7 + x^6 + x + 1
        f = open(dirname(__file__) + '/gost_tables', 'rb')
        self.multtable = pickle.load(f)
        f.close()

        # Константы С для разветки ключа
        self.C = [self.l_transform([0] * 15 + [i]) for i in range(1, 33)]

        # проверим что правильно генерит
        assert self.C[0] == [110, 162, 118, 114, 108, 72, 122, 184, 93, 39, 189, 16, 221, 132, 148, 1]

        # генерим развертку ключа
        self.roundkey = [key[:16], key[16:]]
        self.roundkey = self.roundkey + self.keyschedule(self.roundkey)

    def add_field(self, x, y):
        """суммирование в поле x^8 + x^7 + x^6 + x + 1"""
        return x ^ y

    def sum_field(self, x):
        """Сумма всех элементов x"""
        s = 0
        for a in x:
            s ^= a
        return s

    def mult_field(self, x, y):
        """Перемножение в поле x^8 + x^7 + x^6 + x + 1 """
        p = 0
        while x:
            if x & 1:
                p ^= y
            if y & 0x80:
                y = (y << 1) ^ 0x1C3
            else:
                y <<= 1
            x >>= 1
        return p

    def x_transform(self, x, k):
        """XOR бинарных строк x и k"""
        return [x[i] ^ k[i] for i in range(len(k))]

    def s_transform(self, x):
        """Замена каждого байта x согласно таблице PI"""
        return [self.PI[x[i]] for i in range(len(x))]

    def s_inv_transform(self, x):
        """Замена каждого байта x согласно таблице PI_INV"""
        return [self.PI_INV[i] for i in x]

    def l(self, x):
        """Делает из массива байтов один байт используя заранее посчитанную таблицу"""
        consts = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]
        multiplication = [self.multtable[x[i]][consts[i]] for i in range(len(x))]
        return self.sum_field(multiplication)

    def r_transform(self, x):
        """R transform"""
        return [self.l(x), ] + x[:-1]

    def r_inv_transform(self, x):
        """Inverse R transformation"""
        return x[1:] + [self.l(x[1:] + [x[0], ]), ]

    def l_transform(self, x):
        """Последовательное выполнение R transform 16 раз"""
        for i in range(len(x)):
            x = self.r_transform(x)
        return x

    def l_inv_transform(self, x):
        """Inverse L transformation"""
        for i in range(len(x)):
            x = self.r_inv_transform(x)
        return x

    def f_transform(self, k, a):
        """F transform для развертки ключа"""
        tmp = self.x_transform(k, a[0])
        tmp = self.s_transform(tmp)
        tmp = self.l_transform(tmp)
        tmp = self.x_transform(tmp, a[1])
        return [tmp, a[0]]

    def keyschedule(self, roundkey):
        """Генерирует развертку ключа для раундов"""
        roundkeys = []
        for i in range(4):
            for k in range(8):
                roundkey = self.f_transform(self.C[8 * i + k], roundkey)
            roundkeys.append(roundkey[0])
            roundkeys.append(roundkey[1])
        return roundkeys

    def encrypt(self, m):
        """ Шифрует сообщение m
            Args:
                m: str в 16-ом формате
        """
        m = list(binascii.unhexlify(m))
        for i in range(9):
            m = self.x_transform(m, self.roundkey[i])
            m = self.s_transform(m)
            m = self.l_transform(m)
        m = self.x_transform(m, self.roundkey[9])
        return binascii.hexlify(bytearray(m))

    # Decryption of ciphertext c with key
    def decrypt(self, c):
        """Расшифровывает сообщение с
            Args:
                c: str в 16-ом формате"""
        c = list(binascii.unhexlify(c))
        for i in range(9, 0, -1):
            c = self.x_transform(c, self.roundkey[i])
            c = self.l_inv_transform(c)
            c = self.s_inv_transform(c)
        c = self.x_transform(c, self.roundkey[0])
        return binascii.hexlify(bytearray(c))
        # return c
