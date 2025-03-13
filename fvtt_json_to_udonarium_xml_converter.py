import argparse  # コマンドライン引数を扱うためのモジュール
import json  # JSON データを扱うためのモジュール
import logging  # ログ出力用モジュール
import os  # OS 関連の機能 (ファイルパス操作など) を使うためのモジュール
import sys  # システム関連の機能 (プログラム終了など) を使うためのモジュール
from lxml import etree  # XML を扱うためのモジュール

# ロギングの設定 (エラーメッセージを詳細に出力)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Foundry VTT と D&D 5e システムのバージョン情報 (JSONデータの _stats から取得)
# このスクリプトは以下のバージョンを基に作成されています:
# Foundry VTT core version: 11.315
# D&D 5e system version (systemId: dnd5e): 3.3.1
# これらのバージョン情報は、JSONデータの "_stats" キー内にあります。
# バージョンが異なると、JSONの構造が変更されている可能性があるため、注意が必要です。

def create_resource_element(parent, name, current_value, max_value):
    """
    ユドナリウムの「リソース」要素 (currentValue 属性を持つ) を作成する関数。
    例: <data name="ヒット・ポイント" type="numberResource" currentValue="32">60</data>
    """
    element = etree.SubElement(parent, "data", name=name)
    element.set("currentValue", str(current_value)) # 現在値 (例: 32)
    element.text = str(max_value) # 最大値 (例: 60)
    element.set("type", "numberResource") # type属性 (ユドナリウムでリソースとして扱うために必要)
    return element

def fvtt_json_to_xml(json_data):
    """
    Foundry VTT の JSON データをユドナリウム形式の XML 文字列に変換する関数。
    """
    try:
        root = etree.Element("character")  # ルート要素を作成

        # character data (rootの直下)キャラクターデータを追加
        character_data = etree.SubElement(root, "data", name="character")

        # image data (character data の中)
        image_data = etree.SubElement(character_data, "data", name="image")
        image_identifier = etree.SubElement(image_data, "data", name="imageIdentifier")# ユドナリウムの仕様では、キャラクター画像はimageIdentifierで指定。
        image_identifier.text = ""

        # common data (character data の中)
        common_data = etree.SubElement(character_data, "data", name="common")
        name_element = etree.SubElement(common_data, "data", name="name")
        name_element.text = json_data.get("name", "") #キャラクター名
        
        # サイズ
        size = json_data["system"]["traits"].get("size", "")
        size_element = etree.SubElement(common_data, "data", name="size")
        size_element.text = size

        # detail data (character data の中)
        detail = etree.SubElement(character_data, "data", name="detail")

        # 基本情報
        basic_data = etree.SubElement(detail, "data", name="基本")
        race_name = ""
        for item in json_data.get("items", []): # itemsの中から、
            if item.get("type") == "race":# typeがraceのものを探す
                race_name = item.get("name", "")# raceのnameをrace_nameに入れる
                break
        race_element = etree.SubElement(basic_data, "data", name="種族")
        race_element.text = race_name

        class_names = []
        levels = []
        hit_dices = []
        for item in json_data.get("items", []):
            if item.get("type") == "class":
                class_names.append(item.get("name", ""))
                levels.append(item.get("system", {}).get("levels", 0))
                hit_dices.append(item.get("system", {}).get("hitDice", ""))

        class_element = etree.SubElement(basic_data, "data", name="クラス")
        class_element.text = ", ".join(class_names)# クラス名をカンマ区切りで出力 (例: "ウィザード, バーバリアン"), マルチクラス想定
        level_element = etree.SubElement(basic_data, "data", name="レベル")
        level_element.text = str(sum(levels)) #レベル

        alignment_element = etree.SubElement(basic_data, "data", name="属性")
        alignment_element.text = json_data["system"]["details"].get("alignment", "").replace("属性", "")
        player_element = etree.SubElement(basic_data, "data", name="プレイヤー")
        player_element.text = ""

        # 能力値
        abilities_data = etree.SubElement(detail, "data", name="能力値")
        ability_mapping = { #FoundryVTTのsystem.abilitiesのkeyとユドナリウムのdata nameの対応関係
            "str": "【筋力】",
            "dex": "【敏捷力】",
            "con": "【耐久力】",
            "int": "【知力】",
            "wis": "【判断力】",
            "cha": "【魅力】",
        }

        for en_name, jp_name in ability_mapping.items():
            ability_value = json_data["system"]["abilities"].get(en_name, {}).get("value", 0)
            ability_element = etree.SubElement(abilities_data, "data", name=jp_name)
            ability_element.text = str(ability_value)


        # 行動データ
        action_data = etree.SubElement(detail, "data", name="行動データ")
        ac_element = etree.SubElement(action_data, "data", name="AC")
        ac_element.text = "" #JSONから直接参照で取得できないものは空文字
        create_resource_element(action_data, "ヒット・ポイント",json_data["system"]["attributes"]["hp"].get("value", 0), json_data["system"]["attributes"]["hp"].get("max", 0) )
        create_resource_element(action_data, "一時HP", 0, 0) #固定値

        #ヒットダイス
        hit_dice_info = []
        for i in range(len(levels)):
          if levels[i] > 0 and hit_dices[i]:# レベルとヒットダイスが両方有効な場合
              hit_dice_info.append(f"{levels[i]}{hit_dices[i]}")#レベルとヒットダイスを結合
        hit_dice_str = ", ".join(hit_dice_info)#ヒットダイス情報を文字列に
        hit_dice_element = etree.SubElement(action_data, "data", name="ヒット・ダイス")
        hit_dice_element.text = hit_dice_str

        create_resource_element(action_data, "インスピレーション", 0, 1)

        proficiency_element = etree.SubElement(action_data, "data", name="習熟ボーナス")
        proficiency_element.text = "" #JSONから直接参照で取得できないものは空文字
        spell_attack_element = etree.SubElement(action_data, "data", name="呪文攻撃ロール")
        spell_attack_element.text = "" #JSONから直接参照で取得できないものは空文字
        spell_save_element = etree.SubElement(action_data, "data", name="呪文セーブ")
        spell_save_element.text = "" #JSONから直接参照で取得できないものは空文字
        size_element2 = etree.SubElement(action_data, "data", name="サイズ")
        size_element2.text = size
        speed_element = etree.SubElement(action_data, "data", name="移動速度")
        speed_element.text = "" #JSONから直接参照で取得できないものは空文字
        initiative_element = etree.SubElement(action_data, "data", name="イニシアチブ")
        initiative_element.text = "" #JSONから直接参照で取得できないものは空文字
        initiative_modify_element = etree.SubElement(action_data, "data", name="イニシアチブ修正")
        initiative_modify_element.text = "" #JSONから直接参照で取得できないものは空文字
        condition_element = etree.SubElement(action_data, "data", name="状態異常")
        condition_element.text = "" #JSONから直接参照で取得できないものは空文字

        # 技能
        skills_data = etree.SubElement(detail, "data", name="技能")
        skills_mapping = {
          "acr": "〈軽業〉",
          "ani": "〈動物使い〉",
          "arc": "〈魔法学〉",
          "ath": "〈運動〉",
          "dec": "〈ペテン〉",
          "his": "〈歴史〉",
          "ins": "〈看破〉",
          "itm": "〈威圧〉",
          "inv": "〈捜査〉",
          "med": "〈医術〉",
          "nat": "〈自然〉",
          "prc": "〈知覚〉",
          "prf": "〈芸能〉",
          "per": "〈説得〉",
          "rel": "〈宗教〉",
          "slt": "〈手先の早業〉",
          "ste": "〈隠密〉",
          "sur": "〈生存〉"
        }
        # 項目名だけ追加、値は空
        for jp_skill in skills_mapping.values():
            skill_element = etree.SubElement(skills_data, "data", name=jp_skill)
            skill_element.text = ""

        #セーヴィングスロー
        saving_throws_data = etree.SubElement(detail, "data", name="セーヴィングスロー")
        #項目名だけ追加
        for jp_name in ability_mapping.values():
            saving_throw_element = etree.SubElement(saving_throws_data, "data", name=jp_name)
            saving_throw_element.text = ""


        # 人格的特徴等
        traits_data = etree.SubElement(detail, "data", name="特徴等")
        traits_mapping = {
            "ideal": "尊ぶもの",
            "trait": "人格的特徴",
            "bond": "関わり深いもの",
            "flaw": "弱味",
        }
        for json_name, xml_name in traits_mapping.items():
            trait_value = json_data["system"]["details"].get(json_name, "")
            trait_element = etree.SubElement(traits_data, "data", name=xml_name)
            trait_element.text = trait_value
        background_element = etree.SubElement(traits_data, "data", name="背景")
        background_element.text = ""
        other_settings_element = etree.SubElement(traits_data, "data", name="その他設定など")
        other_settings_element.text = ""
        other_proficiencies_element = etree.SubElement(traits_data, "data", name="その他の習熟と言語")
        other_proficiencies_element.text = ""
        features_element = etree.SubElement(traits_data, "data", name="特徴・特性")
        features_element.text = ""

        #呪文
        spells_data = etree.SubElement(detail, "data", name="呪文")
        for level in range(0, 10): # レベル0（初級呪文）から9まで
            spell_data = json_data["system"]["spells"].get(f"spell{level}")
            lv_data = etree.SubElement(spells_data, "data", name=f"LV{level}" if level > 0 else "初級呪文")

            if level > 0 and spell_data:
                max_slots = spell_data.get("max", 0)
                value_slots = spell_data.get("value", 0)
                # max_slots が 0 の場合は value_slots を最大スロット数として使用
                if max_slots == 0:
                    max_slots = value_slots
                slot_element = etree.SubElement(lv_data, "data", name="スロット")
                slot_element.text = f"{value_slots}/{max_slots}"
            elif level == 0:
                slot_element = etree.SubElement(lv_data, "data", name="スロット")
                slot_element.text = "0/0"

            if level > 0:
                dummy_element = etree.SubElement(lv_data, "data", name="dummy")
                dummy_element.text = ""

        # chat-palette/チャットパレット
        chat_palette = etree.SubElement(root, "chat-palette", dicebot="DungeonsAndDoragons")

        # チャットパレットのテキスト (固定)
        # {}でくくっているのは変数名、ユドナリウムの機能で参照
        # ({【能力値】}-10)/2R は、ユドナリウムの機能で、能力値判定を行うためのロールを生成
        # /2R は割り算の後、四捨五入する。0.5が負の値の場合は値としては切り下げになる。
        chat_palette_text = """1d20+{イニシアチブ}
▼AC:{AC}
移動速度：{移動速度}
■能力値判定=====================================
1d20+({【筋力】}-10)/2R ▼【筋力】能力値判定
1d20+({【敏捷力】}-10)/2R ▼【敏捷力】能力値判定
1d20+({【耐久力】}-10)/2R ▼【耐久力】能力値判定
1d20+({【知力】}-10)/2R ▼【知力】能力値判定
1d20+({【判断力】}-10)/2R ▼【判断力】能力値判定
1d20+({【魅力】}-10)/2R ▼【魅力】能力値判定
■技能============================================
1d20+{〈威圧〉} ▼〈威圧〉能力値判定
1d20+{〈医術〉} ▼〈医術〉能力値判定
1d20+{〈運動〉} ▼〈運動〉能力値判定
1d20+{〈隠密〉} ▼〈隠密〉能力値判定
1d20+{〈軽業〉} ▼〈軽業〉能力値判定
1d20+{〈看破〉} ▼〈看破〉能力値判定
1d20+{〈芸能〉} ▼〈芸能〉能力値判定
1d20+{〈自然〉} ▼〈自然〉能力値判定
1d20+{〈宗教〉} ▼〈宗教〉能力値判定
1d20+{〈生存〉} ▼〈生存〉能力値判定
1d20+{〈説得〉} ▼〈説得〉能力値判定
1d20+{〈捜査〉} ▼〈捜査〉能力値判定
1d20+{〈知覚〉} ▼〈知覚〉能力値判定
1d20+{〈手先の早業〉} ▼〈手先の早業〉能力値判定
1d20+{〈動物使い〉} ▼〈動物使い〉能力値判定
1d20+{〈ペテン〉} ▼〈ペテン〉能力値判定
1d20+{〈魔法学〉} ▼〈魔法学〉能力値判定
1d20+{〈歴史〉} ▼〈歴史〉能力値判定
■呪文============================================
{呪文セーブ} 
1d20+{呪文攻撃ロール} ▼呪文攻撃ロール
■その他============================================
"""

        # 種族
        if race_name:
            chat_palette_text += race_name + "\n"

        # クラス
        if class_names:
            chat_palette_text += ", ".join(class_names) + "\n"

        # アイテム
        for item in json_data.get("items", []):
            item_name = item.get("name", "")
            if item_name:
                chat_palette_text += item_name + "\n"


        chat_palette.text = chat_palette_text.strip()

        return etree.tostring(root, pretty_print=True, encoding="UTF-8", xml_declaration=True).decode("utf-8")

    except Exception as e:
        logger.error(f"変換中に予期しないエラー: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FVTT JSONをユドナリウムXMLに変換します。")
    parser.add_argument("input_json_filename", help="入力JSONファイルのパス")
    # 出力フォルダの引数を追加
    parser.add_argument("-o", "--output_dir", help="出力ディレクトリのパス", default=".") #デフォルトはカレントディレクトリ
    # 出力ファイル名の引数を追加
    parser.add_argument("-f", "--output_file", help="出力ファイル名(拡張子なし).")


    args = parser.parse_args()
    # 使用方法の表示
    print("使用方法: python script.py input.json -o output_directory -f output_filename")

    input_filename = args.input_json_filename

    #出力ファイル名が指定されていなければ、input_filenameから自動生成
    if args.output_file:
        output_filename = args.output_file + ".xml"
    else:
        base_filename, ext = os.path.splitext(os.path.basename(input_filename))
        output_filename = f"1reconverted_{base_filename}.xml"

    #出力ディレクトリの絶対パスを作成
    output_dir = os.path.abspath(args.output_dir)

    #出力ディレクトリが無ければ作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"出力ディレクトリ {output_dir} を作成しました.")

    #出力ファイルのフルパスを作成
    output_path = os.path.join(output_dir, output_filename)

    if not args.input_json_filename.lower().endswith(".json"):
        logger.error("入力ファイルはJSON形式である必要があります。")
        sys.exit(1)

    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"ファイルが見つかりません: {input_filename}")
        logger.error("別のファイルパスを指定するか、ファイルを正しい場所に配置してください。")
        logger.error("プログラムを終了します。")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"JSONデコードエラー: {input_filename} は有効なJSONファイルではありません。")
        logger.error("JSONファイルの内容と形式を確認してください。")
        logger.error("プログラムを終了します。")
        sys.exit(1)

    converted_xml = fvtt_json_to_xml(json_data)
    if converted_xml:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(converted_xml)
        logger.info(f"JSONをXMLに正常に変換しました。出力ファイル: {output_path}")
    else:
        logger.error("変換に失敗しました。")
        logger.error("エラーログを確認し、JSONの構造やコードに問題がないか確認してください。")
