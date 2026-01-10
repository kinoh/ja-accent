#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import itertools as it
from optparse import OptionParser

usage = u"""usage: %prog featurefile
ラベリングされたアクセント型を相対ラベルに置き換える
"""

def abs2rel_text(text):
    output = []
    # 入力ファイルのフォーマット
    # 0.orth, 1.pron, 2.pos1-pos2-pos3-pos4, 3.cType, 4.cForm,
    # 5.lemma-lForm, 6.goshu, 7.iType-iForm-iConType, 8.aType, 9.aConType, 10.aModType,
    # 11.irex, 12.bunsetsu
    # 13.当該形態素のモーラ数、14.アクセント句内の一つ目か否か、15.アクセント句内の最後か否か、
    # 16.アクセント句の形態素数、17.数詞か否か、18.助数詞か否か
    # 19.単独型種類ラベル、20.助数詞ラベル、21.2モーラ以下かどうか、22.重音節を含むか、
    # 23.先頭モーラ、24.第二モーラ、25.単独発声アクセント核位置の一つ前、26.核位置、
    # 27.核位置の一つ後のモーラ、28.末尾の１つ前のモーラ、29.末尾モーラ
    # 30.aType(8)の第一候補、31.aConTypeの助詞・助動詞タイプ（動詞）、32.同形容詞、33.同名詞
    # 一番最後.文中正解アクセントラベル
    for line in text.splitlines():
        if len(line.strip()) == 0:
            output.append("")
            continue
        features = line.split()

        aType1, nmora, ans = features[30], features[13], features[-1]

        # アクセントタイプがなければ、0 とみなしてしまう
        if aType1 == "*": aType1 = 0

        nmora = int(nmora)
        aType1 = int(aType1)
        ans = int(ans)

        if aType1 != 0:
            if ans == 0:
                ans_rel = "non" # アクセント核消失
            elif ans == aType1:
                ans_rel = "same" # アクセント核保存
            elif ans == aType1-1:
                ans_rel = "same-1" # アクセント核が一つ前に移動
            elif ans == nmora:
                ans_rel = "mora" # 最終モーラアクセント型へ（もともと核が最終モーラにあった場合を除く）
            elif ans == 1:
                ans_rel = "atama" # 頭高型へ（１モーラのものを除く）
            elif ans == nmora-1:
                ans_rel = "mora-1" # 最終モーラ一つ前アクセント型へ（もともとその位置にアクセントがあるか、頭高型の場合を除く）
            else:
                ans_rel = str(ans - aType1) # その他は、もとの位置からの移動幅
        else:
            if ans == 0:
                ans_rel = "samenon" # アクセント核消失のまま
            elif ans == nmora:
                ans_rel = "mora" # 最終モーラアクセント型へ
            elif ans == 1:
                ans_rel = "atama" # 頭高型へ（１モーラのものを除く）
            elif ans == nmora-1:
                ans_rel = "mora-1" # 最終モーラ一つ前アクセント型へ（頭高型の場合を除く）
            else:
                ans_rel = str(ans - 0) # その他は、もとの位置からの移動幅

        output.append(" ".join(features[:-1] + [ans_rel]))

    return "\n".join(output)


def main(argv=None):
    parser = OptionParser(usage=usage)
    (options,args) = parser.parse_args(argv)

    if len(args) < 1:
        print("error: too few arguments\n", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    featurefile = open(args[0], encoding="utf-8")
    result = abs2rel_text(featurefile.read())
    if result:
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")


if __name__ == "__main__":
    main()
