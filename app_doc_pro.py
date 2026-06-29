import streamlit as st
import os
import re  
from datetime import datetime

st.set_page_config(page_title="公文智慧管理系統", page_icon="🏛️", layout="wide")

st.title("🏛️ 中華民國標準公文：簽模式案名完美對齊系統 (v52)")
st.markdown("---")

GOV_GLOBAL_DB = {
    "環境部": {"leader": "部長", "zip": "100006", "addr": "臺北市中正區中華路1段83號"},
    "內政部": {"leader": "部長", "zip": "100218", "addr": "臺北市中正區徐州路5號"},
    "行政院": {"leader": "院長", "zip": "100009", "addr": "臺北市中正區忠孝東路1段1號"},
    "宜蘭縣政府": {"leader": "縣長", "zip": "260005", "addr": "宜蘭市縣政一街1號"},
    "宜蘭市公所": {"leader": "市長", "zip": "260002", "addr": "宜蘭市中山路2段432號"},
    "羅東鎮公所": {"leader": "鎮長", "zip": "265003", "addr": "宜蘭縣羅東鎮中興路3號"},
    "臺北市政府環境保護局": {"leader": "局長", "zip": "110204", "addr": "臺北市信義區市府路1號"},
    "宜蘭縣政府環境保護局": {"leader": "局長", "zip": "268015", "addr": "宜蘭縣五結鄉利工二路100號"}
}

def auto_extract_zip(address_text):
    if not address_text:
        return "000"
    for org, info in GOV_GLOBAL_DB.items():
        if info["addr"] in address_text or org in address_text:
            return info["zip"]
    if "五結鄉" in address_text: return "268015"
    if "羅東鎮" in address_text: return "265003"
    if "宜蘭市" in address_text: return "260002"
    
    match = re.match(r'^(\d{3,6})', address_text.strip())
    if match:
        return match.group(1)
    return "260"

def parse_custom_targets(raw_text):
    targets = []
    if not raw_text.strip():
        return targets
    items = [i.strip() for i in re.split(r'[，、,;；]', raw_text) if i.strip()]
    for item in items:
        match = re.search(r'([^(（]+)[(（]([^)）]+)[)）]', item)
        if match:
            name = match.group(1).strip()
            addr = match.group(2).strip()
            targets.append({"name": name, "addr": addr, "is_citizen": True})
        else:
            db_info = GOV_GLOBAL_DB.get(item, {})
            targets.append({
                "name": item, 
                "addr": db_info.get("addr", "隨文發送"), 
                "is_citizen": False
            })
    return targets

if "my_org" not in st.session_state:
    st.session_state["my_org"] = "宜蘭縣政府環境保護局"

st.sidebar.header("⚙️ 完整公務簽核與郵務面板")

my_org = st.sidebar.selectbox("🏢 我方發文機關主體", list(GOV_GLOBAL_DB.keys()), index=list(GOV_GLOBAL_DB.keys()).index(st.session_state["my_org"]))
st.session_state["my_org"] = my_org

st.sidebar.markdown("---")
st.sidebar.subheader("🔄 實務流程階段選擇")
doc_flow_mode = st.sidebar.radio("請選擇公文輸出階段：", [
    "1. 內部請示【簽】模式", 
    "2. 內部簽辦【稿】模式", 
    "3. 簽核核准【正式公文】分頁列印模式"
])

st.sidebar.markdown("---")
st.sidebar.subheader("📋 檔案管理欄位設定")
f_class_no = st.sidebar.text_input("分類號", value="305.42")
f_case_no = st.sidebar.text_input("案次號", value="01")
f_save_years = st.sidebar.text_input("保存年限", value="5年")
f_app_limit = st.sidebar.text_input("應用限制", value="普通")
f_vol_no = st.sidebar.text_input("卷次號", value="01")
f_doc_name = st.sidebar.text_input("案名", value="環境保護稽查與稽催專案管理計畫")

if "【簽】" in doc_flow_mode:
    st.sidebar.markdown("⚠️ *簽為機關內部請示，無需填寫外部正副本受文者*")
    raw_receivers = ""
    raw_copieds = ""
    final_secret = "普通"
    raw_countersign = st.sidebar.text_input("會辦單位（呈現於呈核中欄）", value="主計室、法制科")
else:
    st.sidebar.subheader("📬 收件人設定 (支援機關與民眾)")
    raw_receivers = st.sidebar.text_area("正本受文者", value="環境部、內政部、陳大明(宜蘭市中山路2段100號)", height=70)
    raw_copieds = st.sidebar.text_area("副本受文者", value="宜蘭市公所、羅東鎮公所、李小美(羅東鎮純精路3段50號)", height=70)
    final_secret = st.sidebar.selectbox("密等及解密條件", ["普通", "密", "機密"], index=0)
    final_attachments = st.sidebar.text_input("附件", value="無")
    raw_countersign = st.sidebar.text_input("會辦單位（呈現於呈核中欄）", value="主計室、法制科")

decision_level = st.sidebar.selectbox("內部核決層級", ["第一層決行", "第二層決行", "第三層決行"])

receiver_objects = parse_custom_targets(raw_receivers)
copied_objects = parse_custom_targets(raw_copieds)

st.subheader(f"📝 標準公文簽辦材料區 (發文主體：{my_org})")

col1, col2 = st.columns(2)
with col1:
    user_purpose = st.text_area("🎯 核心主旨：", value="有關重申本轄內隨地拋棄一般廢棄物及煙蒂等行為之稽查執法作為案，請積極結合資源擴大專案巡查並全面取締，以維護環境品質與公眾利益", height=100)
    user_bg = st.text_area("⏳ 說明段：", value="一、依據環境部115年環境保護施政重點方針，暨民眾多次陳情反映本轄核心觀光商圈周邊環境髒亂、煙蒂任意拋棄案辦理。\n二、按廢棄物清理法最新修正條文第27條第1款規定，在指定清除地區內嚴禁有隨地拋棄煙蒂或其他一般廢棄物之行為；倘若違反上開規定者，將依同法第50條第3款之規範，處以新臺幣一千二百元以上六千元以下罰鍰。\n三、部分特定路段任意亂丟煙蒂之情事有日益惡化之趨勢，請各單位務必提高執法密度與強度。", height=220)
with col2:
    if "【簽】" in doc_flow_mode:
        user_actions = st.text_area("📋 擬辦段：", value="一、擬奉 核可後，由本局相關業務課室、環境稽查大隊成立聯合巡查小組，自2026年7月份起針對違規熱點執行高密度巡查與執法取締。\n二、檢附「2026年全國煙蒂不落地稽查執法計畫（草案）」1份，擬奉 核定後據以行文各相關受文機關辦理後續事宜。\n三、本案擬會辦主計室、法制科表示意見。", height=220)
        user_wish = "陳核"
    else:
        user_actions = st.text_area("🛠️ 辦法段：", value="一、請相關業務課室、環境稽查大隊及各鄉鎮市公所清潔隊成立聯合巡查小組，針對特定熱點編排高密度隨機稽查勤務，倘經查獲明確違規事實，一律依法逕行裁處。\n二、請充分利用機關官網、多媒體LED電子看板及社區宣導活動等多元管道，密集廣為宣導廢棄物清理法相關法令，從源頭提升公眾環境保護責任感。\n三、有關執行成效請定期彙整報府憑辦，以利提報環境部續評。", height=220)
        user_wish = st.selectbox("🎯 結尾期望用語：", ["請查照", "請照辦", "請鑒核", "復請查照"])

if st.button("🚀 執行公文智慧對齊與生成", type="primary"):
    clean_purpose = user_purpose.strip().rstrip('，').rstrip('。')
    r_names_text = "、".join([obj["name"] for obj in receiver_objects]) if receiver_objects else "相關單位"
    c_names_text = "".join([obj["name"] for obj in copied_objects]) if copied_objects else "無"
    
    if "【簽】" in doc_flow_mode:
        formatted_body = f"<div style='margin-bottom: 15px; text-align: justify;'><b>【主旨】</b>{clean_purpose}，報請 鑒核。</div>"
        if user_bg:
            formatted_body += "<div style='margin-top: 15px; margin-bottom: 8px;'><b>【說明】</b></div>"
            for line in user_bg.split('\n'):
                if line.strip(): formatted_body += f"<div class='indent-item'>{line.strip()}</div>"
        if user_actions:
            formatted_body += "<div style='margin-top: 15px; margin-bottom: 8px;'><b>【擬辦】</b></div>"
            for line in user_actions.split('\n'):
                if line.strip(): formatted_body += f"<div class='indent-item'>{line.strip()}</div>"
    else:
        formatted_body = f"<div style='margin-bottom: 15px; text-align: justify;'><b>【主旨】</b>{clean_purpose}，{user_wish}。</div>"
        if user_bg:
            formatted_body += "<div style='margin-top: 15px; margin-bottom: 8px;'><b>【說明】</b></div>"
            for line in user_bg.split('\n'):
                if line.strip(): formatted_body += f"<div class='indent-item'>{line.strip()}</div>"
        if user_actions:
            formatted_body += "<div style='margin-top: 15px; margin-bottom: 8px;'><b>【辦法】</b></div>"
            for line in user_actions.split('\n'):
                if line.strip(): formatted_body += f"<div class='indent-item'>{line.strip()}</div>"

    right_meta_html = f"""
    <div style="width: 100%; text-align: right; font-size: 14px; font-family: '標楷體'; color: black; line-height: 1.6; margin-bottom: 25px;">
        <div style="display: inline-block; text-align: left; width: 480px;">
            <div style="width: 100%;">
                <span style="display: inline-block; width: 155px;">☐退稿</span>
                <span style="display: inline-block; width: 155px;"><b>分類號：</b>{f_class_no}</span>
                <span style="display: inline-block; width: 155px;"><b>案次號：</b>{f_case_no}</span>
            </div>
            <div style="width: 100%;">
                <span style="display: inline-block; width: 155px;">☐郵寄</span>
                <span style="display: inline-block; width: 155px; white-space: nowrap;"><b>保存年限：</b>{f_save_years}</span>
                <span style="display: inline-block; width: 155px; white-space: nowrap;"><b>卷次號：</b>{f_vol_no}</span>
            </div>
            <div style="width: 100%;">
                <span style="display: inline-block; width: 155px;">☐自發</span>
                <span style="display: inline-block; width: 155px;"><b>應用限制：</b>{f_app_limit}</span>
                <span style="display: inline-block; width: 155px;"><b>目次號：</b>01</span>
            </div>
            <div style="width: 100%; margin-top: 2px;">
                <span style="display: inline-block; font-weight: bold; width: 55px; text-align: justify; text-align-last: justify;">案名</span>：{f_doc_name}
            </div>
        </div>
    </div>
    """

    sign_top_meta_html = f"""
    <div style="width: 100%; text-align: right; font-size: 14px; font-family: '標楷體'; color: black; line-height: 1.6; margin-bottom: 25px;">
        <div style="display: inline-block; text-align: left; width: 480px;">
            <div style="width: 100%;">
                <span style="display: inline-block; width: 155px;"></span>
                <span style="display: inline-block; width: 155px;"><b>分類號：</b>{f_class_no}</span>
                <span style="display: inline-block; width: 155px;"><b>案次號：</b>{f_case_no}</span>
            </div>
            <div style="width: 100%;">
                <span style="display: inline-block; width: 155px;"></span>
                <span style="display: inline-block; width: 155px; white-space: nowrap;"><b>保存年限：</b>{f_save_years}</span>
                <span style="display: inline-block; width: 155px; white-space: nowrap;"><b>卷次號：</b>{f_vol_no}</span>
            </div>
            <div style="width: 100%;">
                <span style="display: inline-block; width: 155px;"></span>
                <span style="display: inline-block; width: 155px;"><b>應用限制：</b>{f_app_limit}</span>
                <span style="display: inline-block; width: 155px;"><b>目次號：</b>01</span>
            </div>
            <div style="width: 100%; margin-top: 2px;">
                <span style="display: inline-block; width: 155px;"></span>
                <span style="display: inline-block; font-weight: bold; width: 70px; text-align: justify; text-align-last: justify;">案名</span>：{f_doc_name}
            </div>
        </div>
    </div>
    """

    my_org_addr = GOV_GLOBAL_DB.get(my_org, {}).get("addr", "宜蘭縣五結鄉利工二路100號")
    taiwan_year = datetime.now().year - 1911

    contact_right_html = f"""
    <div style="float: right; width: 50%; line-height: 1.6; font-size: 14px; font-family: '標楷體'; color: black; text-align: left; margin-bottom: 20px;">
        地&nbsp;&nbsp;&nbsp;&nbsp;址：{my_org_addr}<br>
        承&nbsp;辦&nbsp;人：科員 張OO<br>
        電&nbsp;&nbsp;&nbsp;&nbsp;話：03-9251000 #123<br>
        電子信箱：chang@mail.gov.tw
    </div>
    <div style="clear: both;"></div>
    """

    display_countersign_units = raw_countersign.strip() if raw_countersign.strip() else "（無會辦）"
    sign_decision_box = f"""
    <div style="width: 100%; border: 2px solid black; margin-top: 40px; font-family: '標楷體'; font-size: 14px; color: black; box-sizing: border-box;">
        <table style="width: 100%; border-collapse: collapse; margin: 0; padding: 0;">
            <tr>
                <td style="width: 33.33%; padding: 12px; vertical-align: top; line-height: 1.8;">
                    <div style="font-weight: bold; font-size: 15px; margin-bottom: 8px; padding-bottom: 3px;">主辦單位（承辦）</div>
                    單位：環境稽查科<br>
                    職稱：科員<br>
                    姓名：張OO
                </td>
                <td style="width: 33.33%; padding: 12px; vertical-align: top; line-height: 1.8;">
                    <div style="font-weight: bold; font-size: 15px; margin-bottom: 8px; padding-bottom: 3px;">會辦單位意見</div>
                    會辦：{display_countersign_units}<br>
                    <div style="margin-top: 15px; color: gray; font-size: 12px;">（請會辦單位簽章）</div>
                </td>
                <td style="width: 33.34%; padding: 12px; vertical-align: top; line-height: 1.8;">
                    <div style="font-weight: bold; font-size: 15px; margin-bottom: 8px; padding-bottom: 3px;">長官批示（決行）</div>
                    <span style="font-size: 11px; color: gray;">層級：[{decision_level}]</span><br>
                    <div style="margin-top: 10px; font-weight: bold; color: #333;">（如擬）</div>
                </td>
            </tr>
        </table>
    </div>
    """

    three_column_decision_box = f"""
    <div style="width: 100%; border: 2px solid black; margin-top: 40px; font-family: '標楷體'; font-size: 14px; color: black; box-sizing: border-box;">
        <table style="width: 100%; border-collapse: collapse; margin: 0; padding: 0;">
            <tr>
                <td style="width: 33.33%; border-right: 1px solid black; padding: 12px; vertical-align: top; line-height: 1.8;">
                    <div style="font-weight: bold; font-size: 15px; margin-bottom: 8px; border-bottom: 1px dashed #000; padding-bottom: 3px;">主辦單位（承辦）</div>
                    單位：環境稽查科<br>
                    職稱：科員<br>
                    姓名：張OO
                </td>
                <td style="width: 33.33%; border-right: 1px solid black; padding: 12px; vertical-align: top; line-height: 1.8;">
                    <div style="font-weight: bold; font-size: 15px; margin-bottom: 8px; border-bottom: 1px dashed #000; padding-bottom: 3px;">會辦單位意見</div>
                    會辦：{display_countersign_units}<br>
                    <div style="margin-top: 15px; color: gray; font-size: 12px;">（請會辦單位簽章）</div>
                </td>
                <td style="width: 33.34%; padding: 12px; vertical-align: top; line-height: 1.8;">
                    <div style="font-weight: bold; font-size: 15px; margin-bottom: 8px; border-bottom: 1px dashed #000; padding-bottom: 3px;">長官批示（決行）</div>
                    <span style="font-size: 11px; color: gray;">層級：[{decision_level}]</span><br>
                    <div style="margin-top: 10px; font-weight: bold; color: #333;">（如擬）</div>
                </td>
            </tr>
        </table>
    </div>
    """

    if "【簽】" in doc_flow_mode:
        sign_header_html = f"""
        <div style="width: 100%; padding-bottom: 12px; margin-top: 5px; margin-bottom: 15px;">
            <table style="border-collapse: collapse; border: none; margin-left: 0; text-align: left;">
                <tr style="border: none;">
                    <td style="padding-right: 20px; border: none; vertical-align: middle; text-align: left;">
                        <span style="font-size: 45px; font-weight: bold; font-family: '標楷體';">簽</span>
                    </td>
                    <td style="font-size: 16px; font-family: '標楷體'; line-height: 1.7; border: none; vertical-align: middle; text-align: left;">
                        中華民國 {taiwan_year} 年 6 月 29 日<br>
                        於 宜蘭縣政府環境保護局環境稽查科
                    </td>
                </tr>
            </table>
        </div>
        """
        
        sign_meta_html = f"""
        <div style="width: 100%; font-size: 15px; margin-bottom: 25px; color: black; font-family: '標楷體'; line-height: 1.8;">
            <b>密等及解密條件或保密期限：</b>{final_secret}
        </div>
        """

        final_document_html = f"""
        <style> .indent-item {{ padding-left: 3.5em; text-indent: -3.50em; margin-bottom: 8px; text-align: justify; }} </style>
        <div style="max-width: 820px; margin: 0 auto; background-color: white; color: black; padding: 40px 40px 50px 50px; font-family: '標楷體'; min-height: 950px; line-height: 1.8;">
            {sign_top_meta_html}
            {sign_header_html}
            {sign_meta_html}
            <div style="color: black; font-size: 16px;">{formatted_body}</div>
            {sign_decision_box}
        </div>
        """
        st.components.v1.html(final_document_html, height=1150, scrolling=True)

    elif "【稿】" in doc_flow_mode:
        title_center_html = f"""
        <div style="width: 100%; text-align: center; margin-bottom: 25px;">
            <h1 style="letter-spacing: 3px; font-size: 26px; font-weight: bold; font-family: '標楷體'; margin: 0;">
                {my_org} &nbsp; 函 &nbsp; (稿)
            </h1>
        </div>
        """
        receiver_block_html = f"""
        <div style="width: 100%; font-size: 15px; margin-bottom: 20px; color: black; font-family: '標楷體'; line-height: 1.8;">
            <b>受文者：</b><span style="font-size: 24px; font-weight: bold;">如行文單位</span><br>
            發文日期：中華民國&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;年&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;月&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;日<br>
            發文字號：<br>
            速&nbsp;&nbsp;&nbsp;&nbsp;別：最速件<br>
            密等及解密條件或保密期限：{final_secret}<br>
            附&nbsp;&nbsp;&nbsp;&nbsp;件：{final_attachments}
        </div>
        """
        distribute_html = f"""
        <div style="font-size: 15px; margin-top: 25px; color: black; font-family: '標楷體';">
            <b>正本：</b>{r_names_text}<br>
            <b>副本：</b>{c_names_text}
        </div>
        """
        final_document_html = f"""
        <style> .indent-item {{ padding-left: 3.5em; text-indent: -3.50em; margin-bottom: 8px; text-align: justify; }} </style>
        <div style="max-width: 820px; margin: 0 auto; background-color: white; color: black; padding: 40px 40px 50px 50px; font-family: '標楷體'; min-height: 950px; line-height: 1.8;">
            {right_meta_html}
            {title_center_html}
            {contact_right_html}
            {receiver_block_html}
            <div style="color: black; margin-top: 15px; font-size: 16px;">{formatted_body}</div>
            {distribute_html}
            <div style="font-size: 19px; font-weight: bold; letter-spacing: 4px; margin-top: 35px; margin-bottom: 10px; color: black;">{GOV_GLOBAL_DB[my_org]['leader']} &nbsp; ○ &nbsp; ○ &nbsp; ○</div>
            {three_column_decision_box}
        </div>
        """
        st.components.v1.html(final_document_html, height=1350, scrolling=True)

    else:
        all_pages_html = ""
        total_targets = receiver_objects + copied_objects
        for idx, obj in enumerate(total_targets):
            target_name = obj["name"]
            target_addr = obj["addr"]
            is_copy_page = obj in copied_objects
            t_zip = auto_extract_zip(target_addr)
            
            page_title_html = f"""
            <div style="width: 100%; text-align: center; margin-bottom: 25px;">
                <h1 style="letter-spacing: 6px; font-size: 28px; font-weight: bold; font-family: '標楷體'; margin: 0;">{my_org} &nbsp; 函</h1>
            </div>
            """
            receiver_block_html = f"""
            <div style="width: 100%; font-size: 15px; margin-bottom: 20px; color: black; font-family: '標楷體'; line-height: 1.8;">
                <b>受文者：</b><span style="font-size: 28px; font-weight: bold; letter-spacing: 1px;">{target_name}</span> <span style="font-size:14px; color:#333; font-weight: normal;">(【{t_zip}】{target_addr})</span><br>
                發文日期：中華民國{taiwan_year}年6月26日<br>
                府環字第1150012345號<br>
                速&nbsp;&nbsp;&nbsp;&nbsp;別：最速件<br>
                密等及解密條件或保密期限：{final_secret}<br>
                附&nbsp;&nbsp;&nbsp;&nbsp;件：{final_attachments}
            </div>
            """
            p_text = f"<span style='font-size:16px; font-weight:bold;'>{target_name}</span>" if not is_copy_page else r_names_text
            c_text = f"<span style='font-size:16px; font-weight:bold;'>{target_name}</span>" if is_copy_page else c_names_text
            
            distribute_html = f"""
            <div style="font-size: 15px; margin-top: 25px; color: black; font-family: '標楷體'; padding-top: 8px;">
                <b>正本：</b>{p_text}<br>
                <b>副本：</b>{c_text}
            </div>
            """
            page_break = "page-break-after: always; margin-bottom: 80px; padding-bottom: 40px;" if idx < (len(total_targets) - 1) else ""
            all_pages_html += f"""
            <div class="gov-page" style="{page_break} font-family: '標楷體'; line-height: 1.8; color: black; background-color: white;">
                {right_meta_html}
                {page_title_html}
                {contact_right_html}
                {receiver_block_html}
                <div style="font-size: 16px; margin-top: 15px;">{formatted_body}</div>
                {distribute_html}
                <div style="font-size: 19px; font-weight: bold; letter-spacing: 4px; margin-top: 55px; color: black;">{GOV_GLOBAL_DB[my_org]['leader']} &nbsp; ○ &nbsp; ○ &nbsp; ○</div>
            </div>
            """
        final_document_html = f"""
        <style> .indent-item {{ padding-left: 3.5em; text-indent: -3.50em; margin-bottom: 8px; text-align: justify; }} </style>
        <div style="max-width: 820px; margin: 0 auto; background-color: white; padding: 20px;">
            {all_pages_html}
        </div>
        """
        st.components.v1.html(final_document_html, height=1800, scrolling=True)