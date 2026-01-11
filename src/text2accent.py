#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import sys

from abs2rel import abs2rel_text
from format_accent import format_accent_text
from mkdata_accent import mkdata_accent_text
from rel2abs import rel2abs_text
from rule import rule_text


def csvsplit(string):
    """Parse CSV format with quoted strings"""
    quote_flag = 0
    buf = ""
    outlist = []
    for letter in string:
        if letter == '"':
            if quote_flag == 0:
                quote_flag = 1
            else:
                quote_flag = 0
        elif letter == "," and quote_flag == 0:
            outlist.append(buf)
            buf = ""
        else:
            buf += letter
    outlist.append(buf)
    return outlist


def split_by_pyopenjtalk(text):
    """Segment text into accent phrases using pyopenjtalk"""
    try:
        import pyopenjtalk
    except ImportError:
        print(
            "pyopenjtalk is required for boundary segmentation. "
            "Please install pyopenjtalk-plus.",
            file=sys.stderr,
        )
        sys.exit(1)

    features = pyopenjtalk.run_frontend(text)
    if not features:
        return ""

    phrases = []
    buffer = []
    for index, feature in enumerate(features):
        if index > 0 and feature["chain_flag"] in (0, -1):
            phrases.append("".join(buffer))
            buffer = []
        buffer.append(feature["string"])

    if buffer:
        phrases.append("".join(buffer))

    return "\n".join(phrases).replace(" ", "")


def parse_args():
    parser = argparse.ArgumentParser(description="Convert text to accent phrase format")
    parser.add_argument(
        "--mecab-dicdir",
        default="../unidic-csj-202512/",
        help="MeCab dictionary directory",
    )
    parser.add_argument(
        "--mecab-userdic",
        default="./tsuki_1.dic",
        help="MeCab user dictionary path (empty to disable)",
    )
    return parser.parse_args()


def run_mecab(text, mecab_dicdir, mecab_userdic):
    """Run MeCab command"""
    command = ["mecab", f"--dicdir={mecab_dicdir}"]
    if mecab_userdic:
        command.append(f"--userdic={mecab_userdic}")
    result = subprocess.run(
        command,
        input=text,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"mecab error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def seikei_from_mecab(text, mecab_dicdir, mecab_userdic):
    """Format MeCab output to match seikei fields"""
    if not text.strip():
        return ""

    output = []
    bunsetsu_flag = "/"
    mecab_output = run_mecab(text, mecab_dicdir, mecab_userdic)

    for line in mecab_output.strip().split("\n"):
        if line == "EOS":
            output.append("")
            bunsetsu_flag = "/"
            continue

        if "\t" not in line:
            continue

        _, features = line.split("\t", 1)
        f = csvsplit(features)

        for ii in range(0, len(f)):
            if f[ii] == "":
                f[ii] = "*"

        irex = "O"
        # Unknown words without pronunciation info should be treated as auxiliary symbols
        if len(f) < 25:
            # Get the surface form from the original line
            surface = line.split("\t")[0] if "\t" in line else "o"
            output.append(
                "%s %s %s-%s-%s-%s %s %s %s-%s %s %s-%s-%s %s %s %s %s %s"
                % (
                    surface,
                    "*",
                    f[0] if len(f) > 0 else "*",
                    f[1] if len(f) > 1 else "*",
                    f[2] if len(f) > 2 else "*",
                    f[3] if len(f) > 3 else "*",
                    f[4] if len(f) > 4 else "*",
                    "*",
                    "*",
                    "*",
                    "*",
                    "*",
                    "*",
                    "*",
                    "*",
                    "*",
                    "*",
                    irex,
                    bunsetsu_flag,
                )
            )
        elif len(f) == 25:
            output.append(
                "%s %s %s-%s-%s-%s %s %s %s-%s %s %s-%s-%s %s %s %s %s %s"
                % (
                    f[8],
                    f[9],
                    f[0],
                    f[1],
                    f[2],
                    f[3],
                    f[4],
                    f[5],
                    f[7],
                    f[6],
                    f[11],
                    f[16],
                    f[17],
                    f[18],
                    f[22],
                    f[23],
                    f[24],
                    irex,
                    bunsetsu_flag,
                )
            )
        elif len(f) >= 29:
            output.append(
                "%s %s %s-%s-%s-%s %s %s %s-%s %s %s-%s-%s %s %s %s %s %s"
                % (
                    f[8],
                    f[9],
                    f[0],
                    f[1],
                    f[2],
                    f[3],
                    f[4],
                    f[5],
                    f[7],
                    f[6],
                    f[12],
                    f[13],
                    f[14],
                    f[17],
                    f[24],
                    f[25],
                    f[26],
                    irex,
                    bunsetsu_flag,
                )
            )

        bunsetsu_flag = "-"

    return "\n".join(output)


def run_crf_test(text, model):
    """Run crf_test command"""
    result = subprocess.run(
        ["crf_test", "-m", model],
        input=text,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"crf_test error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def convert_long_vowel_mark(text):
    """Convert long vowel mark ー to appropriate vowel for VOICEVOX compatibility

    Japanese long vowel rules:
    - After ア column (ア カ サ タ ナ ハ マ ヤ ラ ワ ガ ザ ダ バ パ): ー → ア
    - After イ column (イ キ シ チ ニ ヒ ミ リ ギ ジ ビ ピ): ー → イ
    - After ウ column (ウ ク ス ツ ヌ フ ム ユ ル グ ズ ブ プ): ー → ウ
    - After エ column (エ ケ セ テ ネ ヘ メ レ ゲ ゼ デ ベ ペ): ー → エ
    - After オ column (オ コ ソ ト ノ ホ モ ヨ ロ ヲ ゴ ゾ ド ボ ポ): ー → オ

    Also removes punctuation marks that VOICEVOX doesn't accept.
    """
    # Vowel column mapping based on last character
    vowel_map = {
        'ア': 'ア', 'カ': 'ア', 'サ': 'ア', 'タ': 'ア', 'ナ': 'ア',
        'ハ': 'ア', 'マ': 'ア', 'ヤ': 'ア', 'ラ': 'ア', 'ワ': 'ア',
        'ガ': 'ア', 'ザ': 'ア', 'ダ': 'ア', 'バ': 'ア', 'パ': 'ア',
        'ファ': 'ア', 'ヴァ': 'ア',

        'イ': 'イ', 'キ': 'イ', 'シ': 'イ', 'チ': 'イ', 'ニ': 'イ',
        'ヒ': 'イ', 'ミ': 'イ', 'リ': 'イ', 'ギ': 'イ', 'ジ': 'イ',
        'ビ': 'イ', 'ピ': 'イ', 'ディ': 'イ', 'ティ': 'イ', 'フィ': 'イ', 'ヴィ': 'イ',

        'ウ': 'ウ', 'ク': 'ウ', 'ス': 'ウ', 'ツ': 'ウ', 'ヌ': 'ウ',
        'フ': 'ウ', 'ム': 'ウ', 'ユ': 'ウ', 'ル': 'ウ', 'グ': 'ウ',
        'ズ': 'ウ', 'ブ': 'ウ', 'プ': 'ウ', 'ドゥ': 'ウ', 'トゥ': 'ウ', 'ヴ': 'ウ',
        'ッ': 'ウ',  # Small tsu followed by ー -> ウ

        'エ': 'エ', 'ケ': 'エ', 'セ': 'エ', 'テ': 'エ', 'ネ': 'エ',
        'ヘ': 'エ', 'メ': 'エ', 'レ': 'エ', 'ゲ': 'エ', 'ゼ': 'エ',
        'デ': 'エ', 'ベ': 'エ', 'ペ': 'エ', 'フェ': 'エ', 'ヴェ': 'エ',

        'オ': 'オ', 'コ': 'オ', 'ソ': 'オ', 'ト': 'オ', 'ノ': 'オ',
        'ホ': 'オ', 'モ': 'オ', 'ヨ': 'オ', 'ロ': 'オ', 'ヲ': 'オ',
        'ゴ': 'オ', 'ゾ': 'オ', 'ド': 'オ', 'ボ': 'オ', 'ポ': 'オ',
        'フォ': 'オ', 'ヴォ': 'オ',

        'ン': 'ン',  # ン after ー keeps as ン (shouldn't happen normally)

        # Small kana (for compound sounds)
        'ャ': 'ア', 'ュ': 'ウ', 'ョ': 'オ',
        'ァ': 'ア', 'ィ': 'イ', 'ゥ': 'ウ', 'ェ': 'エ', 'ォ': 'オ',
    }

    # Punctuation marks to remove (VOICEVOX doesn't accept these)
    # Keep 、 (comma) as it creates silence between phrases
    # Keep ？ (full-width question mark) as it can be used at phrase end
    punctuation_to_remove = set('。！…〜～ー・')  # Note: ー will be converted first

    result = []
    i = 0
    while i < len(text):
        char = text[i]

        # Skip punctuation marks (but keep 、 and ？)
        if char in punctuation_to_remove and char != 'ー':
            i += 1
            continue

        if char == 'ー' and result:
            # Look back to find the last kana character (skip ' and /)
            last_kana = None
            for j in range(len(result) - 1, -1, -1):
                if result[j] not in ("'", "/"):
                    # Check for multi-character kana (like ファ, ディ, etc.)
                    if j > 0:
                        two_char = ''.join(result[j-1:j+1])
                        if two_char in vowel_map:
                            last_kana = two_char
                            break
                    last_kana = result[j]
                    break

            if last_kana and last_kana in vowel_map:
                result.append(vowel_map[last_kana])
            else:
                # Fallback: use ウ if we can't determine
                result.append('ウ')
        else:
            result.append(char)
        i += 1

    return ''.join(result)


def normalize_punctuation(text):
    """Normalize punctuation and boundaries for VOICEVOX compatibility"""
    translation = {
        ",": "、",
        "，": "、",
        "?": "？",
    }

    result = []
    for char in text:
        result.append(translation.get(char, char))
    text = "".join(result)

    while "//" in text:
        text = text.replace("//", "/")

    text = text.replace("/、", "、")
    text = text.replace("、/", "、")

    while "、、" in text:
        text = text.replace("、、", "、")

    text = text.replace("/？", "？")
    text = text.replace("'？", "？")

    # Strip / and 、 from start and end, but preserve ？
    text = text.strip("/")
    text = text.strip("、")

    return text


def process_text(input_text: str, mecab_dicdir: str, mecab_userdic: str | None) -> str:
    """Process text and return accent-annotated result.

    Args:
        input_text: Input text to process
        mecab_dicdir: MeCab dictionary directory path
        mecab_userdic: MeCab user dictionary path (None to disable)

    Returns:
        Accent-annotated text
    """
    input_text = input_text.replace("〜", "ー").replace("～", "ー")

    phrase_segmented_text = split_by_pyopenjtalk(input_text)
    formatted_features_2nd = seikei_from_mecab(
        phrase_segmented_text, mecab_dicdir, mecab_userdic
    )
    accent_features = mkdata_accent_text(formatted_features_2nd)
    rule_based_accent = rule_text(accent_features)
    relative_labels = abs2rel_text(rule_based_accent)
    accent_predictions = run_crf_test(relative_labels, "model_accent")
    absolute_labels = rel2abs_text(accent_predictions)
    formatted = format_accent_text(absolute_labels)

    if formatted:
        formatted = convert_long_vowel_mark(formatted)
        result = normalize_punctuation(formatted)
    else:
        result = ""

    return result


def main():
    args = parse_args()
    input_text = sys.stdin.read()

    mecab_dicdir = args.mecab_dicdir
    mecab_userdic = args.mecab_userdic if args.mecab_userdic else None

    result = process_text(input_text, mecab_dicdir, mecab_userdic)
    print(result)


if __name__ == "__main__":
    main()
