#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
from optparse import OptionParser

# モーラ数をカウントする
def x_mora_me( pron, x ):
    nonMoraList = set(u"ァ ィ ゥ ェ ォ ャ ュ ョ".split())
    index_mora = 0
    mora = []
    for p in pron:
        if p not in nonMoraList:
            mora.append(p)
            index_mora += 1
        else:
            mora[index_mora-1] += p
    return mora[x]

usage = u"""usage: %prog datafile
匂坂・宮崎規則でアクセント推定する"""

ref6 = re.compile("F6")
repercent = re.compile("%")
reatmark = re.compile("@")


def rule_text(text):

    # アクセント句を保存するバッファ
    data_buf = []
    # 文節が二つ以上あった場合の退避場所
    data_buf_tmp = []

    # 今見ている形態素までのアクセント核位置
    now_accent = 0
    # 今見ている形態素までの累積モーラ数
    now_nmora = 0
    # 一つ前までの累積モーラ数
    prev_nmora = 0
    # 今見ている形態素までの、助詞・助動詞を省く直前の品詞
    now_pos = ""

    # 文節が２つ繋がってアクセント句ができている場合に、
    # 文節の数を保存するフラグと前の文節のアクセント型モーラ数
    morebunsetsu_flag = 0
    morebunsetsu_accent = 0
    morebunsetsu_nmora = 0

    output = []

    for line in text.split("\n"):
        
        elems = line.strip("\n").split(" ")
        
        #改行がきたら、結果を出力、初期化して次へ
        if len(elems) == 1:

            print_flag = 0

            if morebunsetsu_flag == 1:
                # ２文節目以上だった場合、文節結合規則により now_accent を変更
                if morebunsetsu_accent == 0 and now_accent == 0:
                    now_accent = 0
                elif morebunsetsu_accent == 0 and now_accent != 0:
                    now_accent = morebunsetsu_nmora + now_accent
                elif morebunsetsu_accent != 0 and now_accent == 0:
                    now_accent = morebunsetsu_accent
                elif morebunsetsu_accent != 0 and now_accent != 0:
                    now_accent = morebunsetsu_accent

                for ii in range(0,len(data_buf)):
                    data_buf_tmp.append( data_buf[ii] )
                data_buf = data_buf_tmp
            
            for ii, data in enumerate(data_buf):

                fields = [
                    data["orth"],
                    data["pron"],
                    data["pos"],
                    data["cType"],
                    data["cForm"],
                    data["lemma"],
                    data["goshu"],
                    data["iType"],
                    data["aType"],
                    data["aConType"],
                    data["aModType"],
                    data["irex"],
                    data["bunsetsu"],
                    data["nmora"],
                    data["morph1"],
                    data["morphl"],
                    data["nmorph"],
                    data["issushi"],
                    data["isjosushi"],
                    data["relAType"],
                    data["josushiType"],
                    data["two"],
                    data["juuon"],
                    data["mora1"],
                    data["mora2"],
                    data["mora3"],
                    data["mora4"],
                    data["mora5"],
                    data["mora6"],
                    data["mora7"],
                    data["aType1"],
                    data["aConTypeFV"],
                    data["aConTypeFA"],
                    data["aConTypeFN"],
                    data["MaType1"],
                ]

                # 最後に推定値を出力
                if data["now_nmora"] >= now_accent and print_flag == 0:
                    accent = now_accent - data["prev_nmora"]

                    # 特殊モーラがきたら一つずらす
                    if accent > 0:
                        x_mora = x_mora_me(data["pron"], accent-1 )
                        if x_mora == "ー" or x_mora == "ッ" or x_mora == "ン":
                            accent -= 1

                    # 一番最後に核があるのは、無視すればよい。
                    # アクセント句境界があるので意味がないので。
                    if ii == len(data_buf)-1 and int(data["nmora"]) == accent:
                        accent = 0

                    fields.append(str(accent))
                    print_flag = 1
                else:
                    fields.append("0")

                output.append(" ".join(fields))

            output.append("")
            # initialization
            now_accent = 0
            prev_accent = 0
            now_nmora = 0
            prev_nmora = 0
            now_pos = ""
            prev_pos = ""
            morebunsetsu_flag = 0
            morebunsetsu_accent = 0
            morebunsetsu_nmora = 0
            data_buf = []
            data_buf_tmp = []
            continue
        
        # データを読む
        data = {}
        data["orth"], data["pron"], data["pos"], data["cType"], data["cForm"], \
        data["lemma"], data["goshu"], data["iType"], data["aType"], data["aConType"], \
        data["aModType"], data["irex"], data["bunsetsu"], \
        data["nmora"], data["morph1"], data["morphl"], data["nmorph"], data["issushi"], \
        data["isjosushi"], data["relAType"], data["josushiType"], data["two"], \
        data["juuon"], data["mora1"], data["mora2"], data["mora3"], data["mora4"], \
        data["mora5"], data["mora6"], data["mora7"], data["aType1"], \
        data["aConTypeFV"], data["aConTypeFA"], data["aConTypeFN"], data["MaType1"] = elems


        # 二文節目に入った場合
        # ２つ目の文節がある場合にはデータを初期化
        if data["bunsetsu"] == "/" and len(data_buf) != 0:

            if morebunsetsu_flag == 1:
                # 既に３文節目以上だった場合
                if morebunsetsu_accent == 0 and now_accent == 0:
                    morebunsetsu_accent = 0
                elif morebunsetsu_accent == 0 and now_accent != 0:
                    morebunsetsu_accent = morebunsetsu_nmora + now_accent
                elif morebunsetsu_accent != 0 and now_accent == 0:
                    morebunsetsu_accent = morebunsetsu_accent
                elif morebunsetsu_accent != 0 and now_accent != 0:
                    morebunsetsu_accent = morebunsetsu_accent
            else:
                morebunsetsu_flag = 1
                morebunsetsu_accent = now_accent

            morebunsetsu_nmora += now_nmora
            # data_buf は退避させて、カラにする
            for ii in range(0,len(data_buf)):
                data_buf_tmp.append( data_buf[ii] )
                
            data_buf = []
            now_accent = 0
            prev_accent = 0
            now_nmora = 0
            prev_nmora = 0
            now_pos = ""
            prev_pos = ""

        
        # 品詞の大分類を pos に入れる
        pos = data["pos"].split("-")[0]
        
        # アクセント型の第一候補が未定義の時は、0 型とする。
        if data["aType1"] == "*": data["aType1"] = "0"
        aType1 = int( data["aType1"] )

        # アクセント修飾型として、aModType_type と aModType_value を抽出
        if data["aModType"] != "*":
            aModType_type = data["aModType"].split("@")[0]
            aModType_value = int( data["aModType"].split("@")[1] )

        # アクセント修飾型の規則によって aType1 を変更する
        if data["aModType"] != "*":
            if aModType_type == "M1":
                aType1 = int(data["nmora"]) - aModType_value
            elif aModType_type == "M2":
                if aType1 == 0:
                    aType1 = int(data["nmora"]) - aModType_value
                # else: なにもしない
            elif aModType_type == "M4":
                if aType1 != 0 and aType1 != 1:
                    aType1 = aType1 - aModType_value
                # else: なにもしない
        
        # 品詞ごとの aConType の情報を aConTypeDic に抽出
        aConTypeDic={}
        
        # 「品詞%アクセント結合規則@アクセント価,品詞2%...」を、コンマで区切る
        alist = data["aConType"].split(",")
        # F6 はアクセント価が 2 つあり、カンマで区切られているので、
        # そこだけは結合するというハックをしておく
        for ii in range( 0, len(alist) ):
            if ii >= len(alist): break
            if ref6.search( alist[ii] ) is not None:
                alist[ii] = alist[ii] + "," + alist[ii+1]
                alist.remove( alist[ii+1] )
        for aa in alist:
            if repercent.search(aa) is not None:
                # 品詞%アクセント結合規則@アクセント価
                aConType_pos = aa.split("%")[0]
                aConType_type = aa.split("%")[1].split("@")[0]
                if reatmark.search(aa.split("%")[1]) is not None:
                    # aConType_type が F6 の場合は、"3,4" など複数の数字が入る
                    # それ以外なら数字が入る
                    aConType_value = aa.split("%")[1].split("@")[1]
                    aConTypeDic[ aConType_pos ] = ( aConType_type, aConType_value )
                else:
                    aConTypeDic[ aConType_pos ] = ( aConType_type, 0 )
            else:
                # C* の場合は、% が含まれていない。
                aConType_type = aa
                # type が書かれていない場合には C5 タイプとする
                if aConType_type == "*": aConType_type = "C5"
        
        # モーラ数を更新
        nmora = int( data["nmora"] )
        prev_nmora = now_nmora
        now_nmora += nmora

        # prev_accent を更新
        prev_accent = now_accent

        # 品詞を更新
        prev_pos = now_pos
        # 助詞・助動詞・接尾辞・接頭辞以外が来たら now_pos を更新
        if pos != "助詞" and pos != "助動詞" and pos != "接尾辞" and pos != "接頭辞":
            now_pos = pos
        
        #################################################################
        # 準備 done.
        # ここから具体的に now_accent を変えていく。
        #################################################################

        # 一つ目の形態素だったら、その単独発声アクセント型を初期値とする。
        if len(data_buf) == 0:
            now_accent = aType1

        # 現在の形態素が名詞で、一つ前に接頭辞が来ていた場合、
        # 接頭辞の規則によって accent を変更する。
        if prev_pos == "接頭辞" and now_pos == "名詞":
            if data_buf[-1]["aConType"] == "P1":
                if aType1 == 0 or aType1 == nmora:
                    now_accent = 0
                else:
                    now_accent = prev_nmora + aType1
            elif data_buf[-1]["aConType"] == "P2":
                if aType1 == 0 or aType1 == nmora:
                    now_accent = prev_nmora + 1
                else:
                    now_accent = prev_nmora + aType1
            elif data_buf[-1]["aConType"] == "P4":
                # P4 の場合は、三通りある。えいやと一つに決めた。
                if aType1 == 0 or aType1 == nmora:
                    now_accent = prev_nmora + 1
                else:
                    now_accent = prev_nmora + aType1
            elif data_buf[-1]["aConType"] == "P6":
                now_accent = 0
            elif data_buf[-1]["aConType"] == "P13":
                # P13 の場合は、二通りある。えいやと一つに決めた。
                now_accent = int( data_buf[-1]["aType1"] )
            elif data_buf[-1]["aConType"] == "P14":
                if aType1 == 0 or aType1 == nmora:
                    now_accent = int(data_buf[-1]["aType1"])
                else:
                    now_accent = prev_nmora + aType1
        # 名詞でなかったり、前がなかったり接頭詞ではなかった場合、なにもしない

        # 現在の形態素が助詞・助動詞で、prev_pos のルールがある場合、
        # 自立語+付属語規則で now_accent を移動させる
        if prev_pos in aConTypeDic:
            aConType_type = aConTypeDic[ prev_pos ][0]
            aConType_value = aConTypeDic[ prev_pos ][1]

            # F1 のときはなにもしない
            if aConType_type == "F2":
                if prev_accent == 0:
                    now_accent = prev_nmora + int(aConType_value)
            elif aConType_type == "F3":
                if prev_accent != 0:
                    now_accent = prev_nmora + int(aConType_value)
            elif aConType_type == "F4":
                now_accent = prev_nmora + int(aConType_value)
            elif aConType_type == "F5":
                now_accent = 0
            elif aConType_type == "F6":
                if prev_accent == 0:
                    now_accent = prev_nmora + int(aConType_value.split(",")[0])
                else:
                    now_accent = prev_nmora + int(aConType_value.split(",")[1])

        # 自立語連続の場合の規則
        if prev_pos != "":
            if aConType_type == "C1":
                now_accent = prev_nmora + aType1
            elif aConType_type == "C2":
                now_accent = prev_nmora + 1
            elif aConType_type=="C3":
                now_accent = prev_nmora
            elif aConType_type=="C4":
                now_accent = 0
            elif aConType_type =="C5":
                now_accent = now_accent
                #C5は何もしない

        #数詞の宮崎規則
        if prev_pos != "" and data_buf[-1]["issushi"] == "1" and data["isjosushi"] == "1":
            sushi = data_buf[-1]["iType"].split("-")[2]
            josushi = data["josushiType"]
            orth = data_buf[-1]["orth"]
            
            # 0型となる規則
            if sushi=="N1"and josushi=="g" or \
                   sushi=="N2" and josushi=="g" or orth=="二" and josushi=="g" or \
                   sushi=="N3" and josushi=="g" or orth=="三" and josushi=="g" or \
                   sushi=="N6" and josushi=="g" or orth=="六" and josushi=="g" or \
                   sushi=="N8" and josushi=="g" or orth=="八" and josushi=="g" or \
                   sushi=="N3" and josushi=="d" or orth=="三" and josushi=="d" or \
                   sushi=="N4" and josushi=="d" or orth=="四" and josushi=="d" or \
                   sushi=="N5" and josushi=="d" or orth=="五" and josushi=="d" or \
                   sushi=="N3" and josushi=="c" or orth=="三" and josushi=="c" or \
                   sushi=="N5" and josushi=="c" or orth=="五" and josushi=="c" or \
                   sushi=="N5" and josushi=="b" or orth=="五" and josushi=="b" or \
                   orth=="千" or \
                   orth=="億" or \
                   orth=="万" or \
                   orth=="兆":
                now_accent = 0
            #助数詞の第一音節
            elif sushi=="N0" and josushi=="e" or \
                     sushi=="N1" and josushi=="e" or orth=="一" and josushi=="e" or \
                     sushi=="N2" and josushi=="e" or orth=="二" and josushi=="e" or \
                     sushi=="N3" and josushi=="e" or orth=="三" and josushi=="e" or \
                     sushi=="N5" and josushi=="e" or orth=="五" and josushi=="e" or \
                     sushi=="N6" and josushi=="e" or orth=="六" and josushi=="e" or \
                     sushi=="N8" and josushi=="e" or orth=="八" and josushi=="e" or \
                     sushi=="N1" and josushi=="i" or orth=="一" and josushi=="i" or \
                     sushi=="N2" and josushi=="i" or orth=="二" and josushi=="i" or \
                     sushi=="N5" and josushi=="i" or orth=="五" and josushi=="i" or \
                     sushi=="N6" and josushi=="i" or orth=="六" and josushi=="i" or \
                     sushi=="N3" and josushi=="j" or orth=="三" and josushi=="j" or \
                     sushi=="N4" and josushi=="j" or orth=="四" and josushi=="j" or \
                     sushi=="N5" and josushi=="j" or orth=="五" and josushi=="j" or \
                     sushi=="N9" and josushi=="j" or orth=="九" and josushi=="j" or \
                     sushi=="N1" and josushi=="l" or orth=="一" and josushi=="l" or \
                     sushi=="N2" and josushi=="l" or orth=="二" and josushi=="l" or \
                     sushi=="N5" and josushi=="l" or orth=="五" and josushi=="l" or \
                     sushi=="N6" and josushi=="l" or orth=="六" and josushi=="l" or \
                     sushi=="N8" and josushi=="l" or orth=="八" and josushi=="l" or \
                     sushi=="Nj" and josushi=="l" or orth=="十" and josushi=="l" or \
                     sushi=="Nh" and josushi=="l" or orth=="百" and josushi=="l":
                now_accent = prev_nmora + 1
            #助数詞の最終音節
            elif sushi=="N0"and josushi=="f" or \
                     sushi=="N1" and josushi=="f" or orth=="一" and josushi=="f" or \
                     sushi=="N2" and josushi=="f" or orth=="二" and josushi=="f" or \
                     sushi=="N5" and josushi=="f" or orth=="五" and josushi=="f" or \
                     sushi=="N6" and josushi=="f" or orth=="六" and josushi=="f" or \
                     sushi=="N8" and josushi=="f" or orth=="八" and josushi=="f" or \
                     sushi=="Nj" and josushi=="f" or orth=="十" and josushi=="f" or \
                     sushi=="N1" and josushi=="h" or orth=="一" and josushi=="h" or \
                     sushi=="N6" and josushi=="h" or orth=="六" and josushi=="h" or \
                     sushi=="N8" and josushi=="h" or orth=="八" and josushi=="h" or \
                     sushi=="N1" and josushi=="k" or orth=="一" and josushi=="k" or \
                     sushi=="N2" and josushi=="k" or orth=="二" and josushi=="k" or \
                     sushi=="N4" and josushi=="k" or orth=="四" and josushi=="k" or \
                     sushi=="N6" and josushi=="k" or orth=="六" and josushi=="k" or \
                     sushi=="N7" and josushi=="k" or orth=="七" and josushi=="k" or \
                     sushi=="N8" and josushi=="k" or orth=="八" and josushi=="k" or \
                     sushi=="Nj" and josushi=="k" or orth=="十" and josushi=="k" or \
                     sushi=="Nh" and josushi=="k" or orth=="百" and josushi=="k":
                now_accent = now_nmora
        
        # データを data_buf に保存
        data["now_nmora"] = now_nmora
        data["prev_nmora"] = prev_nmora
        data_buf.append(data)

    return "\n".join(output)


def main(argv=None):
    parser = OptionParser(usage=usage)
    (options,args) = parser.parse_args(argv)

    if len(args) < 1:
        print("Error: too few arguments\n", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    datafile = open(args[0], encoding="utf-8")
    result = rule_text(datafile.read())
    if result:
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")


if __name__ == '__main__':
    main()
