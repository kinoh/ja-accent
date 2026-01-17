#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser

usage = u"""usage: %prog resultfile
Format accent output with / for phrase boundaries and ' for accent nucleus
"""

# それ自身ではモーラ数にカウントされない読み一覧
nonMoraList = set(u"ァ ィ ゥ ェ ォ ャ ュ ョ".split())

def format_phrase(phrase_data):
    """アクセント句をフォーマット"""
    result = []
    mora_count = 0
    total_mora = 0
    nucleus_position = -1  # アクセント句全体の核位置

    # まずアクセント句全体のモーラ数と核位置を計算
    for morph in phrase_data:
        pron = morph['pron']
        accent = morph['accent']

        # 発音形をモーラに分解してモーラ数を数える
        mora_list_temp = []
        i = 0
        while i < len(pron):
            if i + 1 < len(pron) and pron[i + 1] in nonMoraList:
                mora_list_temp.append(pron[i] + pron[i + 1])
                i += 2
            else:
                mora_list_temp.append(pron[i])
                i += 1

        morph_mora_count = len(mora_list_temp)

        # アクセント核の位置を計算（アクセント句全体での位置）
        if accent > 0:
            nucleus_position = total_mora + accent

        total_mora += morph_mora_count

    # モーラを出力
    mora_count = 0
    for morph in phrase_data:
        pron = morph['pron']

        # 発音形をモーラに分解
        mora_list = []
        i = 0
        while i < len(pron):
            if i + 1 < len(pron) and pron[i + 1] in nonMoraList:
                mora_list.append(pron[i] + pron[i + 1])
                i += 2
            else:
                mora_list.append(pron[i])
                i += 1

        # モーラを追加
        for mora in mora_list:
            mora_count += 1
            result.append(mora)
            # 核の直後に'を付ける（ただし、核がアクセント句の最後のモーラでない場合のみ）
            if nucleus_position == mora_count and mora_count < total_mora:
                result.append("'")

    # 核がアクセント句の最後のモーラ、または平板型（nucleus_position == -1）の場合は末尾に'を付ける
    if nucleus_position == -1 or nucleus_position >= total_mora:
        result.append("'")

    # アクセント句境界を示す/を追加
    result.append("/")
    return "".join(result)

def format_accent_text(text):
    auxiliary_keep_boundary = {"ー"}

    # バッファに1アクセント句を保存
    phrase_buffer = []
    output_parts = []
    auxiliary_buffer = []  # 補助記号のバッファ

    for line in text.splitlines():
        if len(line.strip()) == 0:
            # 空行は無視（EOFまで1つの文として処理）
            continue

        features = line.split()
        if len(features) < 36:
            continue

        orth = features[0]  # 書字形
        pron = features[1]  # 発音形
        boundary_flag = features[12]  # 文節境界フラグ（/か-）

        # pron == "*" の場合は補助記号（、など）
        if pron == "*":
            # boundary_flagに基づいて処理を分ける
            # '/'の場合は次のアクセント句の前、'-'の場合は現在のアクセント句の後
            auxiliary_buffer.append((orth, boundary_flag))
            continue

        nmora = int(features[13])  # モーラ数

        # 最後の列が推定アクセント型
        try:
            accent_pos = int(features[-1])
        except ValueError:
            # 数値に変換できない場合は0（平板型）として扱う
            accent_pos = 0

        # アクセント句境界（/）の場合は、前のアクセント句を出力
        if boundary_flag == '/' and phrase_buffer:
            # 前のアクセント句がある場合は出力
            formatted = format_phrase(phrase_buffer)
            # boundary_flag == '-'の補助記号があれば、'/'の前に挿入（/は除去）
            separators = []
            if auxiliary_buffer:
                for aux_orth, aux_boundary in auxiliary_buffer:
                    if aux_boundary == '-':
                        # Keep the phrase boundary for standalone marks that will be normalized later.
                        if aux_orth in auxiliary_keep_boundary:
                            formatted = formatted[:-1] + aux_orth + "/"
                        else:
                            # '/'を除去して補助記号を追加
                            formatted = formatted[:-1] + aux_orth
                    elif aux_boundary == '/':
                        # ？は文末が上がる韻律なので保持、それ以外は、に変換
                        if aux_orth == '？':
                            separators.append('？')
                        else:
                            separators.append('、')
                # boundary_flag == '/'の補助記号は句間に出力
                auxiliary_buffer = []
            output_parts.append(formatted)
            if separators:
                output_parts.extend(separators)
            phrase_buffer = []

        # データを保存
        phrase_buffer.append({
            'orth': orth,
            'pron': pron,
            'nmora': nmora,
            'accent': accent_pos,
            'boundary': boundary_flag
        })

    # 最後に残っているバッファがあれば処理
    if phrase_buffer:
        formatted = format_phrase(phrase_buffer)
        # boundary_flag == '-'の補助記号があれば、'/'の前に挿入（/は除去）
        separators = []
        if auxiliary_buffer and formatted.endswith('/'):
            for aux_orth, aux_boundary in auxiliary_buffer:
                if aux_boundary == '-':
                    # Keep the phrase boundary for standalone marks that will be normalized later.
                    if aux_orth in auxiliary_keep_boundary:
                        formatted = formatted[:-1] + aux_orth + "/"
                    else:
                        # '/'を除去して補助記号を追加
                        formatted = formatted[:-1] + aux_orth
                elif aux_boundary == '/':
                    # ？は文末が上がる韻律なので保持、それ以外は、に変換
                    if aux_orth == '？':
                        separators.append('？')
                    else:
                        separators.append('、')
            # boundary_flag == '/'の補助記号は後で出力
            auxiliary_buffer = []
        output_parts.append(formatted)
        if separators:
            output_parts.extend(separators)

    # 残っている補助記号があれば追加（？は保持、それ以外は、に変換）
    if auxiliary_buffer:
        output_parts.extend(['？' if (b == '/' and o == '？') else ('、' if b == '/' else o) for o, b in auxiliary_buffer])

    if output_parts:
        result = "".join(output_parts)
        # 末尾の/を除去
        if result.endswith('/'):
            result = result[:-1]
        return result
    return ""


def main(argv=None):
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args(argv)

    if len(args) < 1:
        print("error: too few arguments\n", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    resultfile = open(args[0], encoding="utf-8")
    result = format_accent_text(resultfile.read())
    if result:
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")


if __name__ == "__main__":
    main()
