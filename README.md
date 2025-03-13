# fvtt2udonarium - Foundry VTT to ユドナリウム キャラクターコンバーター

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![lxml](https://img.shields.io/badge/lxml-required-brightgreen.svg)](https://lxml.de/)

**非エンジニア向け・3ステップで簡単変換！**  
Foundry VTT のD&D第5版のキャラクターデータjsonをユドナリウムのキャラクターデータ (XML形式) に変換するツールです。

## 概要

このスクリプト `fvtt2udonarium.py` は、Foundry Virtual Tabletop (FVTT) のD&D第5版からエクスポートしたキャラクターデータ (JSON形式) を、ユドナリウム (およびその派生サービス) で読み込み可能な XML 形式に変換します。

**🌟 主な特徴：**

*   Foundry VTT のキャラクターデータ (JSON) をユドナリウムのキャラクターデータ (XML) に変換
*   基本的なキャラクター情報 (名前、サイズ、種族、クラス、レベル、属性、ヒットポイントなど) を変換
*   技能、セーヴィングスローの項目名を変換 (値は空欄)
*   特徴 (Traits)、所持品 (Items) の一部を変換
*   チャットパレットを自動生成 (ユドナリウムで変数として利用可能な形式)
*   出力ディレクトリ、出力ファイル名を指定可能

## 🚀 簡単3ステップ
1. **JSONエクスポート**：Foundry VTTからキャラデータを出力
2. **変換実行**：このツールでXMLファイルを生成
3. **ドラッグ＆ドロップ**：ユドナリウムにXMLを読み込み

**変換できるデータ (一部):**

*   キャラクター名
*   サイズ
*   種族
*   クラス
*   レベル (マルチクラス対応、合計レベルを表示)
*   属性 (アライメント)
*   能力値
*   ヒットポイント (現在値/最大値)
*   ヒットダイス (各クラスのレベルとダイスタイプ。例: `5d6`, `3d8, 2d10`)
*   インスピレーション
*   技能 (項目名のみ)
*   セーヴィングスロー (項目名のみ)
*   特徴 (一部)
*   所持品 (アイテム名)
*   呪文スロット (各レベルの使用回数/最大回数)
*   チャットパレット (基本的な能力値判定、技能判定などのダイスロールコマンドを自動生成)

**変換できない/部分的にしか変換できないデータ:**

*   習熟ボーナス、呪文攻撃ロール、呪文セーブDC (JSON データに直接含まれていないため、空欄になります)
*   移動速度、イニシアチブ (JSON データに直接含まれていないため、空欄になります)
*   詳細な呪文データ (呪文の説明など)
*   特徴 (Traits) や所持品 (Items) の詳細な説明
*   画像 (imageIdentifier は空欄になります)
*   その他、Foundry VTT 固有のデータ (モジュールによる拡張など)

**注意点:**

*   このスクリプトは、Foundry VTT の **D&D 5e システム** の特定のバージョン (core: 11.315, dnd5e: 3.3.1) でエクスポートされた JSON データでの動作を想定して作成されています。
*   Foundry VTT や D&D 5e システムのバージョンアップ、使用しているモジュールによっては、JSON のデータ構造が変わり、正しく変換できなくなる可能性があります。
*   ユドナリウム、およびその互換ソフトのバージョンによっては、生成された XML ファイルが読み込めない、または一部のデータが正しく表示されない可能性があります。
*   変換できないデータや、ユドナリウムでサポートされていないデータは、XML 上では空欄になるか、一部の情報のみが出力されます。必要に応じて、変換後にユドナリウム上で手動で編集してください。

## 使い方

### 1. 必要なもの

*   Python 3.6 以降 (3.9 以降を推奨)
*   lxml ライブラリ (`pip install lxml` でインストール)
*   Foundry VTT からエクスポートしたキャラクターデータ (JSON形式)

### 2. インストール (Python 環境の準備)

1.  **Python のインストール:**
    *   Python がインストールされていない場合は、Python の公式サイト (https://www.python.org/downloads/) からインストーラーをダウンロードし、インストールしてください。
    *   インストール時に、「Add Python to PATH」 (または類似のオプション) にチェックを入れることを推奨します。
2.  **lxml ライブラリのインストール:**
    *   コマンドプロンプト (Windows) またはターミナル (macOS/Linux) を開きます。
    *   以下のコマンドを実行します:
        ```bash
        pip install lxml
        ```
    *   (もし `pip` コマンドが見つからない場合は、`python -m pip install lxml` または `python3 -m pip install lxml` を試してください)

### 3. スクリプトのダウンロード

この `fvtt2udonarium.py` ファイルを、適当なフォルダに保存してください (例: デスクトップ上の `fvtt2udonarium` フォルダ)。

### 4. JSON ファイルのエクスポート (Foundry VTT)

1.  Foundry VTT で、変換したいキャラクターのキャラクターシートを開きます。
2.  キャラクターシートの右上にある、縦に3つ点が並んだアイコン(...)をクリックします。
3.  表示されたメニューから「JSON形式でエクスポート」を選択します。
4.  JSON ファイルを保存します (例: `fvtt-Actor-キャラクター名-XXXXXXXX.json`)。

### 5. スクリプトの実行

1.  コマンドプロンプト (Windows) またはターミナル (macOS/Linux) を開きます。
2.  `cd` コマンドで、`fvtt2udonarium.py` を保存したフォルダに移動します。
    *   例 (デスクトップ上の `fvtt2udonarium` フォルダに保存した場合):
        ```bash
        cd Desktop/fvtt2udonarium
        ```
3.  以下のコマンドを実行します:

    ```bash
    python fvtt2udonarium.py [JSONファイルパス] [オプション]
    ```

    *   **`[JSONファイルパス]`**:  Foundry VTT からエクスポートした JSON ファイルのパスを指定します (例: `fvtt-Actor-コルナヴァール-4HAzzxsaPjdYbwk2.json`)。
    *   **`[オプション]`**: (省略可)
        *   `-o` または `--output_dir`:  出力ディレクトリを指定します (例: `-o output`)。指定しない場合は、スクリプトを実行したディレクトリ (カレントディレクトリ) に出力されます。
        *   `-f` または `--output_file`: 出力ファイル名を指定します (例: `-f KorNavar`)。拡張子 (.xml) は不要です。指定しない場合は、`1reconverted_[JSONファイル名].xml` という名前で出力されます。

    *   **実行例:**
         ```bash
         python fvtt2udonarium.py fvtt-Actor-MyCharacter-ABC123xyz.json -o converted_xml -f MyCharacter
         ```
         (この例では、`fvtt-Actor-MyCharacter-ABC123xyz.json` を変換し、`converted_xml` フォルダ内に `MyCharacter.xml` という名前で保存します)

4.  変換が成功すると、指定した出力ディレクトリ (またはカレントディレクトリ) に XML ファイルが生成されます。

### 6. ユドナリウムでの読み込み

1.  ユドナリウム (または派生サービス) をウェブブラウザ上で開きます。
2.  ブラウザ上で開いているルーム内にXMLをドロップします。

## トラブルシューティング

*   **エラーが出て変換できない:**
    *   Python と lxml が正しくインストールされているか確認してください。
    *   入力ファイルが正しい JSON 形式であるか確認してください (Foundry VTT からエクスポートした直後のファイルであるか)。
    *   Foundry VTT や D&D 5e システムのバージョンが異なる場合、JSON の構造が変わっている可能性があります。

*   **XML ファイルがユドナリウムで読み込めない:**
    *   ユドナリウム (または派生サービス) のバージョンが古い場合、新しい形式の XML を読み込めないことがあります。
    *   XML ファイルが破損している可能性があります。再度変換を試してみてください。

## 免責事項

*   このスクリプトは、Foundry VTT の D&D 5e システムの特定のバージョンでエクスポートされた JSON データでの動作を想定して作成されています。
*   Foundry VTT、D&D 5e システム、ユドナリウム (および互換ソフト) のバージョンアップ、使用しているモジュールによっては、正しく動作しなくなる可能性があります。

## 更新履歴
* 2024-03-14: 初版作成

## 例

### 入力JSONファイル

```json
{
  "name": "冒険者太郎",
  "type": "character",
  "system": {
    "abilities": {
      "str": { "value": 15 },
      "dex": { "value": 14 },
      "con": { "value": 13 },
      "int": { "value": 12 },
      "wis": { "value": 10 },
      "cha": { "value": 8 }
    },
    "attributes": {
      "hp": { "value": 30, "max": 30 }
    },
    "details": {
      "alignment": "中立",
      "race": "人間"
    },
    "spells": {
      "spell1": { "value": 2, "max": 2 }
    }
  },
  "items": [
    { "type": "race", "name": "人間" },
    { "type": "class", "name": "戦士", "system": { "levels": 3, "hitDice": "d10" } },
    { "name": "ロングソード", "type": "weapon", "system": { "description": { "value": "鋭い剣" } } }
  ]
}
```
### 出力XMLファイル
XML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<character>
  <data name="character">
    <data name="image">
      <data name="imageIdentifier"></data>
    </data>
    <data name="common">
      <data name="name">冒険者太郎</data>
      <data name="size"></data>
    </data>
    <data name="detail">
      <data name="基本">
        <data name="種族">人間</data>
        <data name="クラス">戦士</data>
        <data name="レベル">3</data>
        <data name="属性">中立</data>
        <data name="プレイヤー"></data>
      </data>
      <data name="能力値">
        <data name="【筋力】">15</data>
        <data name="【敏捷力】">14</data>
        <data name="【耐久力】">13</data>
        <data name="【知力】">12</data>
        <data name="【判断力】">10</data>
        <data name="【魅力】">8</data>
      </data>
      <data name="行動データ">
        <data name="AC"></data>
        <data name="ヒット・ポイント" currentValue="30" type="numberResource">30</data>
        <data name="一時HP" currentValue="0" type="numberResource">0</data>
        <data name="ヒット・ダイス">3d10</data>
        <data name="インスピレーション" currentValue="0" type="numberResource">1</data>
        <data name="習熟ボーナス"></data>
        <data name="呪文攻撃ロール"></data>
        <data name="呪文セーブ"></data>
        <data name="サイズ"></data>
        <data name="移動速度"></data>
        <data name="イニシアチブ"></data>
        <data name="イニシアチブ修正"></data>
        <data name="状態異常"></data>
      </data>
      <data name="技能">
        <data name="〈軽業〉"></data>
        <data name="〈動物使い〉"></data>
        <data name="〈魔法学〉"></data>
        <data name="〈運動〉"></data>
        <data name="〈ペテン〉"></data>
        <data name="〈歴史〉"></data>
        <data name="〈看破〉"></data>
        <data name="〈威圧〉"></data>
        <data name="〈捜査〉"></data>
        <data name="〈医術〉"></data>
        <data name="〈自然〉"></data>
        <data name="〈知覚〉"></data>
        <data name="〈芸能〉"></data>
        <data name="〈説得〉"></data>
        <data name="〈宗教〉"></data>
        <data name="〈手先の早業〉"></data>
        <data name="〈隠密〉"></data>
        <data name="〈生存〉"></data>
      </data>
      <data name="セーヴィングスロー">
        <data name="【筋力】"></data>
        <data name="【敏捷力】"></data>
        <data name="【耐久力】"></data>
        <data name="【知力】"></data>
        <data name="【判断力】"></data>
        <data name="【魅力】"></data>
      </data>
      <data name="特徴等">
        <data name="尊ぶもの"></data>
        <data name="人格的特徴"></data>
        <data name="関わり深いもの"></data>
        <data name="弱味"></data>
        <data name="背景"></data>
        <data name="その他設定など"></data>
        <data name="その他の習熟と言語"></data>
        <data name="特徴・特性"></data>
      </data>
      <data name="呪文">
        <data name="初級呪文">
          <data name="スロット">0/0</data>
        </data>
        <data name="LV1">
          <data name="スロット">2/2</data>
          <data name="dummy"></data>
        </data>
        <data name="LV2">
          <data name="スロット">0/0</data>
          <data name="dummy"></data>
        </data>
        <data name="LV3">
          <data name="スロット">0/0</data>
          <data name="dummy"></data>
        </data>
        <data name="LV4">
          <data name="スロット">0/0</data>
          <data name="dummy"></data>
        </data>
        <data name="LV5">
          <data name="スロット">0/0</data>
          <data name="dummy"></data>
        </data>
        <data name="LV6">
          <data name="スロット">0/0</data>
          <data name="dummy"></data>
        </data>
        <data name="LV7">
          <data name="スロット">0/0</data>
          <data name="dummy"></data>
        </data>
        <data name="LV8">
          <data name="スロット">0/0</data>
          <data name="dummy"></data>
        </data>
        <data name="LV9">
          <data name="スロット">0/0</data>
          <data name="dummy"></
```
