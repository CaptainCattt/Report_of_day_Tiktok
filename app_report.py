import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io


def process_tiktok_daily_report(df_all, df_income):
    df_income.columns = df_income.columns.str.strip()
    df_income["ABS_Total_Fees"] = df_income["Total fees"].abs()

    df_income["Classify"] = (
        df_income["Related order ID"]
        .duplicated(keep=False)
        .map({True: "Duplicate", False: "Not Duplicate"})
    )

    df_income["Paydouble"] = df_income.duplicated(
        subset=["Related order ID", "Order/adjustment ID"], keep=False
    ).map({True: "Yes", False: "No"})

    df_income["Order/adjustment ID"] = df_income["Order/adjustment ID"].astype(str)
    df_income["Related order ID"] = df_income["Related order ID"].astype(str)

    # Bước 1: Đánh dấu cờ để xử lý
    df_income["OID_start7"] = (
        df_income["Order/adjustment ID"].astype(str).str.startswith("7")
    )
    df_income["Not_Order_Type"] = df_income["Type"].astype(str) != "Order"

    # Bước 2: Đếm số lần xuất hiện của Related order ID
    df_income["RID_count"] = df_income.groupby("Related order ID")[
        "Related order ID"
    ].transform("count")

    # Bước 3: Xác định loại đơn theo logic
    grouped = df_income.groupby("Related order ID")
    is_compensation = grouped["OID_start7"].transform("any") | grouped[
        "Not_Order_Type"
    ].transform("any")
    is_doublepaid = (df_income["RID_count"] > 1) & ~is_compensation

    # Bước 4: Gán nhãn
    df_income["Actually Order Type"] = "Normal"  # Mặc định là Normal
    df_income.loc[is_compensation, "Actually Order Type"] = "Compensation"
    df_income.loc[is_doublepaid, "Actually Order Type"] = "DoublePaid"

    # Bước 5: Xoá cột phụ nếu muốn
    df_income.drop(columns=["OID_start7", "Not_Order_Type", "RID_count"], inplace=True)

    # Data all

    df_all["Order ID"] = df_all["Order ID"].astype(str)

    # Chuẩn hóa cột Province và Country cho df_all
    df_all["Province"] = df_all["Province"].str.replace(
        r"^(Tỉnh |Tinh )", "", regex=True
    )
    df_all["Province"] = df_all["Province"].str.replace(
        r"^(Thanh pho |Thành phố |Thành Phố )", "", regex=True
    )

    df_all["Country"] = df_all["Country"].replace(
        {
            "Viêt Nam",
            "Vietnam",
            "The Socialist Republic of Viet Nam",
            "Socialist Republic of Vietnam",
        },
        "Việt Nam",
    )

    df_all["Province"] = df_all["Province"].replace(
        {
            "Ba Ria– Vung Tau": "Bà Rịa - Vũng Tàu",
            "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
            "Ba Ria - Vung Tau": "Bà Rịa - Vũng Tàu",
            "Bac Giang": "Bắc Giang",
            "Bac Lieu": "Bạc Liêu",
            "Bac Ninh": "Bắc Ninh",
            "Ben Tre": "Bến Tre",
            "Binh Dinh": "Bình Định",
            "Binh Duong": "Bình Dương",
            "Binh Duong Province": "Bình Dương",
            "Binh Phuoc": "Bình Phước",
            "Binh Thuan": "Bình Thuận",
            "Ca Mau": "Cà Mau",
            "Ca Mau Province": "Cà Mau",
            "Can Tho": "Cần Thơ",
            "Phố Cần Thơ": "Cần Thơ",
            "Da Nang": "Đà Nẵng",
            "Da Nang City": "Đà Nẵng",
            "Phố Đà Nẵng": "Đà Nẵng",
            "Dak Lak": "Đắk Lắk",
            "Đắc Lắk": "Đắk Lắk",
            "Ðắk Nông": "Đắk Nông",
            "Đắk Nông": "Đắk Nông",
            "Dak Nong": "Đắk Nông",
            "Dong Nai": "Đồng Nai",
            "Dong Nai Province": "Đồng Nai",
            "Dong Thap": "Đồng Tháp",
            "Dong Thap Province": "Đồng Tháp",
            "Ha Nam": "Hà Nam",
            "Ha Noi": "Hà Nội",
            "Ha Noi City": "Hà Nội",
            "Phố Hà Nội": "Hà Nội",
            "Hai Phong": "Hải Phòng",
            "Phố Hải Phòng": "Hải Phòng",
            "Ha Tinh": "Hà Tĩnh",
            "Hau Giang": "Hậu Giang",
            "Hô-Chi-Minh-Ville": "Hồ Chí Minh",
            "Ho Chi Minh": "Hồ Chí Minh",
            "Ho Chi Minh City": "Hồ Chí Minh",
            "Kota Ho Chi Minh": "Hồ Chí Minh",
            "Hoa Binh": "Hòa Bình",
            "Hoà Bình": "Hòa Bình",
            "Hung Yen": "Hưng Yên",
            "Khanh Hoa": "Khánh Hòa",
            "Khanh Hoa Province": "Khánh Hòa",
            "Khánh Hoà": "Khánh Hòa",
            "Kien Giang": "Kiên Giang",
            "Kiến Giang": "Kiên Giang",
            "Long An Province": "Long An",
            "Nam Dinh": "Nam Định",
            "Nghe An": "Nghệ An",
            "Ninh Binh": "Ninh Bình",
            "Ninh Thuan": "Ninh Thuận",
            "Quang Binh": "Quảng Bình",
            "Quang Tri": "Quảng Trị",
            "Quang Nam": "Quảng Nam",
            "Quang Ngai": "Quảng Ngãi",
            "Quang Ninh": "Quảng Ninh",
            "Quang Ninh Province": "Quảng Ninh",
            "Soc Trang": "Sóc Trăng",
            "Tay Ninh": "Tây Ninh",
            "Thai Binh": "Thái Bình",
            "Thanh Hoa": "Thanh Hóa",
            "Thanh Hoá": "Thanh Hóa",
            "Hai Duong": "Hải Dương",
            "Thừa Thiên Huế": "Thừa Thiên-Huế",
            "Thua Thien Hue": "Thừa Thiên-Huế",
            "Vinh Long": "Vĩnh Long",
            "Tra Vinh": "Trà Vinh",
            "Vinh Phuc": "Vĩnh Phúc",
            "Cao Bang": "Cao Bằng",
            "Lai Chau": "Lai Châu",
            "Ha Giang": "Hà Giang",
            "Lam Dong": "Lâm Đồng",
            "Lao Cai": "Lào Cai",
            "Phu Tho": "Phu Tho",
            "Phu Yen": "Phú Yên",
            "Thai Nguyen": "Thái Nguyên",
            "Son La": "Sơn La",
            "Tuyen Quang": "Tuyên Quang",
            "Yen Bai": "Yên Bái",
            "Dien Bien": "Điện Biên",
            "Tien Giang": "Tiền Giang",
        }
    )

    # Chuẩn hóa SKU Category
    df_all["SKU Category"] = df_all["Seller SKU"]
    df_all["SKU Category"] = df_all["SKU Category"].str.replace(
        r"^(COMBO-SC-ANHDUC|COMBO-SC-NGOCTRINH)", "COMBO-SC", regex=True
    )

    date_columns = [
        "Created Time",
        "Paid Time",
        "RTS Time",
        "Shipped Time",
        "Delivered Time",
        "Cancelled Time",
    ]

    # Ép kiểu về datetime
    df_all[date_columns] = df_all[date_columns].apply(
        lambda col: pd.to_datetime(col, errors="coerce", format="%d/%m/%Y %H:%M:%S")
    )

    # Loại bỏ giờ, giữ lại phần ngày (vẫn là kiểu datetime)
    for col in date_columns:
        df_all[col] = df_all[col].dt.normalize()

    df_merged = pd.merge(
        df_income,
        df_all,
        how="left",
        right_on="Order ID",
        left_on="Related order ID",
    )

    Don_quyet_toan = df_merged
    So_don_quyet_toan = len(Don_quyet_toan["Related order ID"].drop_duplicates())

    # Hoan thanh
    Don_hoan_thanh = df_merged[
        (df_merged["Total revenue"] > 0)
        & (df_merged["Actually Order Type"] == "Normal")
    ]
    So_Don_hoan_thanh = len(Don_hoan_thanh["Related order ID"].drop_duplicates())

    # Dieu chinh
    Don_dieu_chinh = df_merged[(df_merged["Type"] != "Order")]
    So_don_dieu_chinh = Don_dieu_chinh["Order/adjustment ID"].count()

    # Dieuchinh tru phi
    Don_dieu_chinh_tru_phi = df_merged[
        (df_merged["Type"] == "Deductions incurred by seller")
    ]
    So_Don_dieu_chinh_tru_phi = Don_dieu_chinh_tru_phi["Order/adjustment ID"].count()

    # Dieu chinh san den bu
    Don_dieu_chinh_san_den_bu = df_merged[
        (df_merged["Type"].isin(["Logistics reimbursement", "Platform reimbursement"]))
    ]
    So_Don_dieu_chinh_san_den_bu = Don_dieu_chinh_san_den_bu[
        "Order/adjustment ID"
    ].count()

    # Don thanh toan truoc
    Don_thanh_toan_truoc = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Actually Order Type"] == "DoublePaid")
    ]
    So_don_thanh_toan_truoc = len(
        Don_thanh_toan_truoc["Order/adjustment ID"].drop_duplicates()
    )

    # Don hoan tra
    Don_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Cancelation/Return Type"] == "Return/Refund")
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Classify"] == "Not Duplicate")
    ]
    So_Don_hoan_tra = Don_hoan_tra["Order/adjustment ID"].count()

    # Don boom
    Don_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
    ]
    So_Don_boom = Don_boom["Order/adjustment ID"].count()

    # Đếm số lượng sản phẩm theo SKU Category
    SCx1_tiktok_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "SC-450g") & (df_merged["Total revenue"] > 0)
    ]

    SCx2_tiktok_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "SC-x2-450g") & (df_merged["Total revenue"] > 0)
    ]

    SC_combo_tiktok_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "COMBO-SC") & (df_merged["Total revenue"] > 0)
    ]

    SCx1_tiktok_quyet_toan = df_merged[(df_merged["SKU Category"] == "SC-450g")]

    SCx2_tiktok_quyet_toan = df_merged[(df_merged["SKU Category"] == "SC-x2-450g")]

    SCxCombo_tiktok_quyet_toan = df_merged[(df_merged["SKU Category"] == "COMBO-SC")]

    so_luong_SCx1_tiktok_hoan_thanh = SCx1_tiktok_hoan_thanh["Quantity"].sum()
    so_luong_SCx2_tiktok_hoan_thanh = SCx2_tiktok_hoan_thanh["Quantity"].sum()
    so_luong_SC_combo_tiktok_hoan_thanh = SC_combo_tiktok_hoan_thanh["Quantity"].sum()
    so_luong_SCx1_tiktok_quyet_toan = SCx1_tiktok_quyet_toan["Quantity"].sum()
    so_luong_SCx2_tiktok_quyet_toan = SCx2_tiktok_quyet_toan["Quantity"].sum()
    so_luong_SCxCombo_tiktok_quyet_toan = SCxCombo_tiktok_quyet_toan["Quantity"].sum()

    return (
        so_luong_SCx1_tiktok_hoan_thanh,
        so_luong_SCx2_tiktok_hoan_thanh,
        so_luong_SC_combo_tiktok_hoan_thanh,
        so_luong_SCx1_tiktok_quyet_toan,
        so_luong_SCx2_tiktok_quyet_toan,
        so_luong_SCxCombo_tiktok_quyet_toan,
        So_Don_boom,
        So_Don_hoan_tra,
        So_don_thanh_toan_truoc,
        So_Don_dieu_chinh_san_den_bu,
        So_Don_dieu_chinh_tru_phi,
        So_don_dieu_chinh,
        So_Don_hoan_thanh,
        So_don_quyet_toan,
        Don_quyet_toan,
        Don_hoan_thanh,
        Don_boom,
        Don_dieu_chinh,
        Don_hoan_tra,
        Don_dieu_chinh_tru_phi,
        Don_dieu_chinh_san_den_bu,
        Don_thanh_toan_truoc,
    )


import streamlit as st
import pandas as pd
import plotly.express as px

# --- Giao diện Streamlit ---
st.set_page_config(page_title="REPORT DAILY OF TIKTOK", layout="wide")
st.markdown(
    """
    <div style='text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px;'>
        <img src='https://icons8.com/icon/118638/tiktok' width='40'/>
        <h1 style='color: black; margin: 0;'>REPORT DAILY OF TIKTOK</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br><br>", unsafe_allow_html=True)  # Tạo khoảng cách sau tiêu đề

# Tạo các cột cho upload file
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        "<h3 style='text-align: center;'>📥 Upload File All Orders Of Tiktok</h3>",
        unsafe_allow_html=True,
    )
    file_all = st.file_uploader(
        "Chọn file tất cả đơn hàng TikTok", type=["xlsx", "xls"], key="tiktok_all"
    )

with col2:
    st.markdown(
        "<h3 style='text-align: center;'>📥 Upload File Income Of Tiktok</h3>",
        unsafe_allow_html=True,
    )
    file_income = st.file_uploader(
        "Chọn file doanh thu TikTok", type=["xlsx", "xls"], key="tiktok_income"
    )

# Khởi tạo trạng thái nếu chưa có
if "processing" not in st.session_state:
    st.session_state.processing = False

# Nút xử lý
import streamlit as st

# Tùy chỉnh kích thước và căn giữa nút
st.markdown(
    """
    <style>
        .center-button {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .button-style {
            font-size: 20px;
            padding: 15px 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .button-style:hover {
            background-color: #45a049;
        }
    </style>

""",
    unsafe_allow_html=True,
)

# Nút Xử lý dữ liệu
with st.container():
    st.markdown('<div class="center-button">', unsafe_allow_html=True)
    process_btn = st.button(
        "🔍 Xử lý dữ liệu",
        key="process_data",
        disabled=st.session_state.processing,
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

if st.button("🔁 Reset", use_container_width=True):
    st.session_state.clear()
    st.rerun()


if process_btn:
    if not file_all or not file_income:
        st.warning("Vui lòng upload cả 2 file!")
    else:
        with st.spinner("⏳ Đang xử lý dữ liệu, vui lòng chờ..."):
            # Đọc dữ liệu từ file upload
            df_all = pd.read_excel(file_all)
            df_income = pd.read_excel(file_income)

            # Process dữ liệu
            (
                so_luong_SCx1_tiktok_hoan_thanh,
                so_luong_SCx2_tiktok_hoan_thanh,
                so_luong_SC_combo_tiktok_hoan_thanh,
                so_luong_SCx1_tiktok_quyet_toan,
                so_luong_SCx2_tiktok_quyet_toan,
                so_luong_SCxCombo_tiktok_quyet_toan,
                So_Don_boom,
                So_Don_hoan_tra,
                So_don_thanh_toan_truoc,
                So_Don_dieu_chinh_san_den_bu,
                So_Don_dieu_chinh_tru_phi,
                So_don_dieu_chinh,
                So_Don_hoan_thanh,
                So_don_quyet_toan,
                Don_quyet_toan,
                Don_hoan_thanh,
                Don_boom,
                Don_dieu_chinh,
                Don_hoan_tra,
                Don_dieu_chinh_tru_phi,
                Don_dieu_chinh_san_den_bu,
                Don_thanh_toan_truoc,
            ) = process_tiktok_daily_report(df_all, df_income)

            st.session_state["Don_quyet_toan"] = Don_quyet_toan
            st.session_state["Don_hoan_thanh"] = Don_hoan_thanh
            st.session_state["Don_thanh_toan_truoc"] = Don_thanh_toan_truoc
            st.session_state["Don_boom"] = Don_boom
            st.session_state["Don_hoan_tra"] = Don_hoan_tra
            st.session_state["Don_dieu_chinh_tru_phi"] = Don_dieu_chinh_tru_phi
            st.session_state["Don_dieu_chinh_san_den_bu"] = Don_dieu_chinh_san_den_bu
            st.session_state["Don_dieu_chinh"] = Don_dieu_chinh

            # Tạo các bảng thống kê
            bang_thong_ke_don_hang_tiktok = pd.DataFrame(
                {
                    "ĐƠN QUYẾT TOÁN": [So_don_quyet_toan],
                    "ĐƠN ĐIỀU CHỈNH": [So_don_dieu_chinh],
                    "ĐƠN THANH TOÁN TRƯỚC": [So_don_thanh_toan_truoc],
                    "ĐƠN HOÀN THÀNH": [So_Don_hoan_thanh],
                    "ĐƠN BOOM": [So_Don_boom],
                    "ĐƠN HOÀN TRẢ": [So_Don_hoan_tra],
                    "ĐƠN ĐC TRỪ PHÍ": [So_Don_dieu_chinh_tru_phi],
                    "ĐƠN ĐC SÀN ĐỀN BÙ": [So_Don_dieu_chinh_san_den_bu],
                },
                index=["Tiktok"],
            )

            bang_thong_ke_so_luong_tiktok = pd.DataFrame(
                {
                    "SL SP": [
                        so_luong_SCx1_tiktok_hoan_thanh
                        + so_luong_SCx2_tiktok_hoan_thanh
                        + so_luong_SC_combo_tiktok_hoan_thanh * 2,
                        so_luong_SCx1_tiktok_quyet_toan
                        + so_luong_SCx2_tiktok_quyet_toan
                        + so_luong_SCxCombo_tiktok_quyet_toan * 2,
                    ],
                    "SCx1": [
                        so_luong_SCx1_tiktok_hoan_thanh,
                        so_luong_SCx1_tiktok_quyet_toan,
                    ],
                    "SCx2": [
                        so_luong_SCx2_tiktok_hoan_thanh,
                        so_luong_SCx2_tiktok_quyet_toan,
                    ],
                    "SCxCOMBO": [
                        so_luong_SC_combo_tiktok_hoan_thanh,
                        so_luong_SCxCombo_tiktok_quyet_toan,
                    ],
                },
                index=["HOÀN THÀNH", "QUYẾT TOÁN"],
            )

            # Vẽ các biểu đồ
            labels = [
                "ĐƠN QUYẾT TOÁN",
                "ĐƠN ĐIỀU CHỈNH",
                "ĐƠN THANH TOÁN TRƯỚC",
                "ĐƠN ĐC SÀN ĐỀN BÙ",
                "ĐƠN HOÀN THÀNH",
                "ĐƠN BOOM",
                "ĐƠN HOÀN TRẢ",
                "ĐƠN ĐC TRỪ PHÍ",
            ]
            tiktok_values = bang_thong_ke_don_hang_tiktok.loc["Tiktok", labels].values

            df_bar = pd.DataFrame({"Loại đơn hàng": labels, "Số lượng": tiktok_values})

            # Biểu đồ cột
            fig_bar_tiktok = px.bar(
                df_bar,
                x="Loại đơn hàng",
                y="Số lượng",
                title="Số lượng các loại đơn hàng TikTok",
                text_auto=True,
                labels={"Loại đơn hàng": "Loại đơn", "Số lượng": "Số đơn"},
            )

            # Biểu đồ tròn Hoàn Thành
            fig_pie_hoan_thanh = px.pie(
                names=["SCx1", "SCx2", "SC COMBO"],
                values=[
                    so_luong_SCx1_tiktok_hoan_thanh,
                    so_luong_SCx2_tiktok_hoan_thanh,
                    so_luong_SC_combo_tiktok_hoan_thanh,
                ],
                title="Tỉ lệ sản phẩm HOÀN THÀNH TikTok",
                hole=0.4,
            )

            # Biểu đồ tròn Quyết Toán
            fig_pie_quyet_toan = px.pie(
                names=["SCx1", "SCx2", "SC COMBO"],
                values=[
                    so_luong_SCx1_tiktok_quyet_toan,
                    so_luong_SCx2_tiktok_quyet_toan,
                    so_luong_SCxCombo_tiktok_quyet_toan,
                ],
                title="Tỉ lệ sản phẩm QUYẾT TOÁN TikTok",
                hole=0.4,
            )

            # Lưu vào session_state
            st.session_state["bang_thong_ke_don_hang_tiktok"] = (
                bang_thong_ke_don_hang_tiktok
            )
            st.session_state["bang_thong_ke_so_luong_tiktok"] = (
                bang_thong_ke_so_luong_tiktok
            )
            st.session_state["fig_bar_tiktok"] = fig_bar_tiktok
            st.session_state["fig_pie_hoan_thanh"] = fig_pie_hoan_thanh
            st.session_state["fig_pie_quyet_toan"] = fig_pie_quyet_toan
            st.session_state.processing = True

# --- Hiển thị kết quả nếu đã xử lý ---
if st.session_state.processing:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='text-align: center; color: #FF9800;'>📊 KẾT QUẢ THỐNG KÊ</h3>",
        unsafe_allow_html=True,
    )
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📋 Bảng Thống Kê Đơn Hàng")
        st.dataframe(st.session_state["bang_thong_ke_don_hang_tiktok"])

    with col2:
        st.markdown("#### 📈 Biểu Đồ Số Lượng Đơn Hàng")
        st.plotly_chart(st.session_state["fig_bar_tiktok"], use_container_width=True)

    # Hiển thị thống kê sản phẩm
    st.markdown("### 📊 SỐ LƯỢNG SẢN PHẨM")
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("#### 📋 Bảng Thống Kê Sản Phẩm")
        st.dataframe(st.session_state["bang_thong_ke_so_luong_tiktok"])

    with col5:
        st.markdown("#### 📈 Biểu Đồ Hoàn Thành")
        st.plotly_chart(
            st.session_state["fig_pie_hoan_thanh"], use_container_width=True
        )

    with col6:
        st.markdown("#### 📈 Biểu Đồ Quyết Toán")
        st.plotly_chart(
            st.session_state["fig_pie_quyet_toan"], use_container_width=True
        )

    st.markdown("### 🔍 Xem chi tiết theo loại đơn hàng")


# Danh sách các loại đơn
ds_loai_don = [
    "ĐƠN QUYẾT TOÁN",
    "ĐƠN HOÀN THÀNH",
    "ĐƠN THANH TOÁN TRƯỚC",
    "ĐƠN ĐIỀU CHỈNH",
    "ĐƠN BOOM",
    "ĐƠN HOÀN TRẢ",
    "ĐƠN ĐC TRỪ PHÍ",
    "ĐƠN ĐC SÀN ĐỀN BÙ",
]

# Hiển thị selectbox và cập nhật session_state
loai_don = st.selectbox("📦 Chọn loại đơn hàng để xem chi tiết:", ds_loai_don)


# Cập nhật lựa chọn vào session_state
st.session_state["loai_don_selected"] = loai_don

# Mapping loại đơn sang DataFrame trong session_state
mapping = {
    "ĐƠN QUYẾT TOÁN": st.session_state.get("Don_quyet_toan", pd.DataFrame()),
    "ĐƠN HOÀN THÀNH": st.session_state.get("Don_hoan_thanh", pd.DataFrame()),
    "ĐƠN THANH TOÁN TRƯỚC": st.session_state.get(
        "Don_thanh_toan_truoc", pd.DataFrame()
    ),
    "ĐƠN BOOM": st.session_state.get("Don_boom", pd.DataFrame()),
    "ĐƠN HOÀN TRẢ": st.session_state.get("Don_hoan_tra", pd.DataFrame()),
    "ĐƠN ĐC TRỪ PHÍ": st.session_state.get("Don_dieu_chinh_tru_phi", pd.DataFrame()),
    "ĐƠN ĐC SÀN ĐỀN BÙ": st.session_state.get(
        "Don_dieu_chinh_san_den_bu", pd.DataFrame()
    ),
    "ĐƠN ĐIỀU CHỈNH": st.session_state.get("Don_dieu_chinh", pd.DataFrame()),
}

# Lấy dữ liệu theo loại đơn đã chọn
df_chi_tiet = mapping.get(loai_don, pd.DataFrame())

# Hiển thị kết quả
if not df_chi_tiet.empty:
    st.markdown(f"#### 📋 Danh sách chi tiết {loai_don}")
    st.dataframe(df_chi_tiet)
else:
    st.info("Không có dữ liệu cho loại đơn này.")
