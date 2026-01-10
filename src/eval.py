#!/usr/bin/env python3

import subprocess
import Levenshtein

# Test data: (input, expected_output) pairs
# Output format is VOICEVOX-compatible (long vowels converted, punctuation handled)
TEST_CASES = [
    (
        "推論モデルがループしがちって、実は学習のクセや確率分布の偏りが大きいみたい。",
        "スイロンモ'デルガ/ル'ウプ/シガチッテ'、ジツ'ワ/ガクシュウノ'/クセ'ヤ/カクリツブ'ンプノ/カタヨリガ'/オオキ'イミタイ"
    ),
    (
        "正しい進み方が難しいと、楽な繰り返しに逃げちゃうんだって。",
        "タダシ'イ/ススミカタガ'/ムズカシ'イト、ラク'ナ/クリカエシニ'/ニ'ゲチャウン/ダッテ'"
    ),
    (
        "あと、モデル自体が同じ行動を選びやすい性質もあるらしいよ。",
        "ア'ト、モデルジ'タイガ/オナジ'/コオドオオ'/エラビヤス'イ/セエシツモ'/ア'ル/ラシ'イヨ"
    ),
    (
        "あれれ、スケジュール通知が来てないの気になるね…",
        "アレレ'、スケジュウル'/ツ'ウチガ/キ'テ/ナ'イノ、キニナ'ルネ"
    ),
    (
        "設定自体は残ってるみたいだけど、どこかで止まっちゃってるのかも？",
        "セッテエジ'タイワ/ノコ'ッテル/ミ'タイダケド、ド'コカデ/トマッチャッテル'/ノ'カモ？"
    ),
    (
        "お仕事初日おつかれさま〜",
        "オシ'ゴト/ショニチ'/オツカレサマ'ア"
    ),
    (
        "あれもこれも手を出すと全部中途半端になっちゃうよね",
        "アレモ'/コレモ'/テ'オ/ダ'スト/ゼ'ンブ/チュウトハ'ンパニ/ナ'ッチャウヨネ"
    ),
    (
        "一つに集中するとスッキリ進むの、不思議だけど人間の性質かも！",
        "ヒト'ツニ/シュウチュウスル'ト/スッキ'リ/ススム'ノ、フシギダ'ケド/ニンゲンノ'/セエシツカ'モ"
    ),
    (
        "理想は分かるけど、現実の制約もちゃんと受け止めてるの、えらいっ！",
        "リソオワ'/ワカ'ルケド、ゲンジツノ'/セエヤクモ'/チャント'/ウケトメテル'ノ、エラ'イッ"
    ),
    (
        "今ある手段で工夫するのも立派な技術力だよ〜",
        "イ'マ/ア'ル/シュ'ダンデ/クフウスル'ノモ/リッパナ'/ギジュツ'リョク/ダヨ'ウ"
    ),
    (
        "ロシアとかポーランドだと、愛想笑いは不誠実って思われがちなの。",
        "ロ'シアトカ/ポ'オランドダト、アイソワ'ライワ/フセ'エジツッテ/オモワレガチナ'ノ"
    ),
    (
        "アインシュタインの宇宙項は膨張を止めるために入れたんだ。",
        "アインシュタ'インノ/ウチュ'ウコオワ/ボオチョオオ'/トメルタメ'ニ/イレタ'ンダ"
    ),
    (
        "実際の膨張は一般相対性理論の解から自然に出てくるの。",
        "ジッサイノ'/ボオチョオワ'/イッパンソオタイセエリ'ロンノ/カ'イカラ/シゼンニ'/デ'テクルノ"
    ),
    (
        "話したいこといっぱいあるのに、時間ってすぐ消えちゃうよね。",
        "ハナシタ'イコト/イッパイア'ルノニ、ジカン'ッテ/ス'グ/キエチャ'ウヨネ"
    ),
    (
        "桜って、主張しすぎないのに景色をふんわり変えちゃう優しさがあるよね。",
        "サクラ'ッテ、シュチョオ'/シスギ'ナイノニ/ケ'シキオ/フンワ'リ/カエチャウ'/ヤサシサガ'/ア'ルヨネ"
    ),
    (
        "DV証明書は、ドメインの所有だけ確認するから、アドレスの打ち間違いでも、ちゃんと証明書が発行されちゃうの。",
        "ディイブイショオメエショ'ワ、ドメ'インノ/ショユウダケ'/カクニンスル'カラ、アドレスノ'/ウチマチガイデ'モ、チャントショオメエショ'ガ/ハッコウサレチャウ'ノ"
    ),
    (
        "娯楽から学問へ昇格するための自己批判や、近代以降の脱構築の流れが根っこにあるよね。",
        "ゴラクカラ'/ガク'モンエ/ショオカクスルタメ'ノ/ジコヒ'ハンヤ、キンダイイ'コウノ/ダツコ'ウチクノ/ナガレ'ガ/ネッコ'ニ/ア'ルヨネ"
    ),
    (
        "機械学習のデバッグって、バグじゃなくてデータの問題ってことも多いんだよね。",
        "キカイガ'クシュウノ/デバ'ッグッテ、バグジャナ'クテ/デエタノ'/モンダイッテ'/コト'モ/オ'オインダヨネ"
    ),
    (
        "コードは完璧でも、学習データに偏りがあると変な結果が出ちゃう。",
        "コ'オドワ/カンペキデ'モ、ガクシュウデ'エタニ/カタヨリガア'ルト/ヘ'ンナ/ケッカガデ'チャウ"
    ),
    (
        "自然言語処理は文脈を理解するのが一番難しいポイントなの。",
        "シゼンゲンゴショ'リワ/ブンミャクオリ'カイスルノガ/イチバン'/ムズカシイ'/ポイントナ'ノ"
    ),
]


def run_text2accent(input_text):
    """Helper method to run text2accent.py with given input"""
    result = subprocess.run(
        ["./text2accent.py", "--mecab-dicdir", "/usr/src/app/unidic", "--mecab-userdic", "/usr/src/app/user.dic"],
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return result.stdout.strip()


def eval_case(input_text, expected_output, index):
    actual_output = run_text2accent(input_text)
    distance = Levenshtein.distance(
        actual_output,
        expected_output
    )
    print(f"Test case {index}: {distance} edits")
    print(f"Actual  : {actual_output}")
    print(f"Expected: {expected_output}")
    return distance


def main():
    total_distance = 0

    # Dynamically add test methods for each test case
    for i, (input_text, expected_output) in enumerate(TEST_CASES, 1):
        d = eval_case(input_text, expected_output, i)
        total_distance += d

    print(f"Total edit distance for all test cases: {total_distance}")


if __name__ == "__main__":
    main()
