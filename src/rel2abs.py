#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import itertools as it
from optparse import OptionParser

usage = u"""usage: %prog resultfile
相対アクセントラベルをアクセント型に置き換える
"""

def rel2abs_text(text):
    output = []
    # 入力ファイルのフォーマット
    # 0.orth, 1.pron, 2.pos1-pos2-pos3-pos4, 3.cType, 4.cForm, 5.lemma-lForm,
    # 6.goshu, 7.iType-iForm-iConType, 8.aType, 9.aConType, 10.aModType, 11.irex, 12.bunsetsu
    # 13.当該形態素のモーラ数、14.アクセント句内の一つ目か否か、15.アクセント句内の最後か否か、
    # 16.アクセント句の形態素数、17.数詞か否か、18.助数詞か否か
    # 19.単独型種類ラベル、20.助数詞ラベル、21.2モーラ以下かどうか、22.重音節を含むか、
    # 23.先頭モーラ、24.第二モーラ、25.単独発声アクセント核位置の一つ前、26.核位置、
    # 27.核位置の一つ後のモーラ、28.末尾の１つ前のモーラ、29.末尾モーラ
    # 30.aType(8)の第一候補、31.aConTypeの助詞・助動詞タイプ（動詞）、32.同形容詞、33.同名詞
    # 37.文中正解アクセントラベル
    # 38.推定した文中アクセントラベル
    for line in text.splitlines():
        if len(line.strip()) == 0:
            output.append("")
            continue
        features = line.split()

        pron, aType1, nmora, ans, hyp = features[1], features[30], features[13], features[-2], features[-1]

        nmora = int(nmora)

        if aType1 == "*": aType1 = 0
        aType1 = int(aType1)

        # for ans
        if aType1 != 0:
            if ans == "non":
                ans_abs = 0
            elif ans == "same":
                ans_abs = aType1
            elif ans == "mora":
                ans_abs = nmora
            elif ans == "same-1":
                ans_abs = aType1-1
            elif ans == "atama":
                ans_abs = 1
            elif ans == "mora-1":
                ans_abs = nmora-1
            else:
                try:
                    ans_abs = int(ans) + aType1
                except:
                    ans_abs = aType1
        else:
            if ans == "samenon":
                ans_abs = 0
            elif ans == "mora":
                ans_abs = nmora
            elif ans == "atama":
                ans_abs = 1
            elif ans == "mora-1":
                ans_abs = nmora-1
            else:
                try:
                    ans_abs = int(ans)
                except:
                    ans_abs = aType1

        # for hyp
        if aType1 != 0:
            if hyp == "non":
                hyp_abs = 0
            elif hyp == "same":
                hyp_abs = aType1
            elif hyp == "mora":
                hyp_abs = nmora
            elif hyp == "same-1":
                hyp_abs = aType1-1
            elif hyp == "atama":
                hyp_abs = 1
            elif hyp == "mora-1":
                hyp_abs = nmora-1
            else:
                try:
                    hyp_abs = int(hyp) + aType1
                except:
                    hyp_abs = aType1
        else:
            if hyp == "samenon":
                hyp_abs = 0
            elif hyp == "mora":
                hyp_abs = nmora
            elif hyp == "atama":
                hyp_abs = 1
            elif hyp == "mora-1":
                hyp_abs = nmora-1
            else:
                try:
                    hyp_abs = int(hyp)
                except:
                    hyp_abs = aType1

        output.append(" ".join(features[:-2] + [str(ans_abs), str(hyp_abs)]))

    return "\n".join(output)


def main(argv=None):
    parser = OptionParser(usage=usage)
    (options,args) = parser.parse_args(argv)

    if len(args) < 1:
        print("error: too few arguments\n", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    resultfile = open(args[0], encoding="utf-8")
    result = rel2abs_text(resultfile.read())
    if result:
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")


if __name__ == "__main__":
    main()
