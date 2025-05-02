import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io


def process_tiktok_daily_report(df_all, df_income):

    VonX1 = 43741.24
    VonX2 = 46041.24
    VonCombo = 89782.48

    VonBTHP_0CAY = 24024.00
    VonBTHP_CAY = 24024.00
    VonBTHP_COMBO = 24024.00

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
    df_all["SKU Category"] = df_all["Seller SKU"].copy()

    # Danh sách các mẫu thay thế
    replacements = {
        r"^(COMBO-SC-ANHDUC|COMBO-SC-NGOCTRINH|COMBO-SC-MIX|SC_COMBO_MIX|SC_COMBO_MIX_LIVESTREAM|COMBO-SC_LIVESTREAM)$": "COMBO-SC",
        r"^SC_X1$": "SC-450g",
        r"^SC_X2$": "SC-x2-450g",
        r"^(SC_COMBO_X1|COMBO-CAYVUA-X1|SC_COMBO_X1_LIVESTREAM|COMBO-SCX1|COMBO-SCX1_LIVESTREAM)$": "COMBO-SCX1",
        r"^(SC_COMBO_X2|COMBO-SIEUCAY-X2|SC_COMBO_X2_LIVESTREAM|COMBO-SCX2|COMBO-SCX2_LIVESTREAM)$": "COMBO-SCX2",
        r"^(BTHP-Cay-200gr|BTHP_Cay)$": "BTHP-CAY",
        r"^(BTHP-200gr|BTHP_KhongCay)$": "BTHP-0CAY",
        r"^(BTHP_COMBO_MIX|BTHP003_combo_mix)$": "BTHP-COMBO",
        r"^(BTHP_COMBO_KhongCay|BTHP003_combo_kocay)$": "BTHP-COMBO-0CAY",
        r"^(BTHP_COMBO_Cay|BTHP003_combo_cay)$": "BTHP-COMBO-CAY",
        r"^BTHP-COMBO\+SC_X1$": "COMBO_BTHP_SCx1",
        r"^BTHP-COMBO\+SC_X2$": "COMBO_BTHP_SCx2",
        r"^BTHP_COMBO_MIX\+SC_X1$": "COMBO_BTHP_SCx1",
        r"^BTHP_COMBO_MIX\+SC_X2$": "COMBO_BTHP_SCx2",
        r"^(BTHP-2Cay-2KhongCay)$": "COMBO_4BTHP",
    }

    for pattern, replacement in replacements.items():
        df_all["SKU Category"] = df_all["SKU Category"].str.replace(
            pattern, replacement, regex=True
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

    Tong_tien_quyet_toan = df_income["Total settlement amount"].sum()

    Tong_tien_hoan_thanh = df_income[df_income["Total revenue"] > 0][
        "Total settlement amount"
    ].sum()

    Tong_phi = df_income[df_income["Total settlement amount"] < 0][
        "Total settlement amount"
    ].sum()

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
    So_don_dieu_chinh = len(Don_dieu_chinh["Related order ID"].drop_duplicates())

    # Dieuchinh tru phi
    Don_dieu_chinh_tru_phi = df_merged[
        (df_merged["Type"] == "Deductions incurred by seller")
    ]
    So_Don_dieu_chinh_tru_phi = len(
        Don_dieu_chinh_tru_phi["Related order ID"].drop_duplicates()
    )

    # Dieu chinh san den bu
    Don_dieu_chinh_san_den_bu = df_merged[
        (df_merged["Type"].isin(["Logistics reimbursement", "Platform reimbursement"]))
    ]
    So_Don_dieu_chinh_san_den_bu = len(
        Don_dieu_chinh_san_den_bu["Related order ID"].drop_duplicates()
    )

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
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
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

    # Số lượng
    SC_X1_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "SC-450g")
    ]

    SC_X2_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "SC-x2-450g")
    ]

    SC_combo_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "COMBO-SC")
    ]

    So_luong_SC_X1_boom = SC_X1_boom["Quantity"].sum()
    So_luong_SC_X2_boom = SC_X2_boom["Quantity"].sum()
    So_luong_SC_combo_boom = SC_combo_boom["Quantity"].sum()

    SC_X1_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "SC-450g")
    ]

    SC_X2_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "SC-x2-450g")
    ]

    SC_COMBO_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "COMBO-SC")
    ]

    SC_X1_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "SC-450g")
        )
    ]

    SC_X2_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "SC-x2-450g")
        )
    ]

    SC_Combo_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "COMBO-SC")
        )
    ]

    So_luong_SC_X1_den_bu = SC_X1_den_bu["Sku Quantity of return"].sum()
    So_luong_SC_X2_den_bu = SC_X2_den_bu["Sku Quantity of return"].sum()
    So_luong_SC_Combo_den_bu = SC_Combo_den_bu["Sku Quantity of return"].sum()

    So_luong_SC_X1_hoan_tra = SC_X1_hoan_tra["Sku Quantity of return"].sum()
    So_luong_SC_X2_hoan_tra = SC_X2_hoan_tra["Sku Quantity of return"].sum()
    So_luong_SC_combo_hoan_tra = SC_COMBO_hoan_tra["Sku Quantity of return"].sum()

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

    so_luong_SCx1_tiktok_hoan_thanh = SCx1_tiktok_hoan_thanh["Quantity"].sum()
    so_luong_SCx2_tiktok_hoan_thanh = SCx2_tiktok_hoan_thanh["Quantity"].sum()
    so_luong_SC_combo_tiktok_hoan_thanh = SC_combo_tiktok_hoan_thanh["Quantity"].sum()

    # BÁNH TRÁNG và COMBO mới
    COMBO_SCx1_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "COMBO-SCX1") & (df_merged["Total revenue"] > 0)
    ]

    COMBO_SCx2_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "COMBO-SCX2") & (df_merged["Total revenue"] > 0)
    ]

    so_luong_COMBO_SCx1_hoan_thanh = COMBO_SCx1_hoan_thanh["Quantity"].sum()
    so_luong_COMBO_SCx2_hoan_thanh = COMBO_SCx2_hoan_thanh["Quantity"].sum()

    COMBO_SCx1_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "COMBO-SCX1")
        )
    ]

    COMBO_SCx2_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "COMBO-SCX2")
        )
    ]

    so_luong_COMBO_SCx1_den_bu = COMBO_SCx1_den_bu["Sku Quantity of return"].sum()
    so_luong_COMBO_SCx2_den_bu = COMBO_SCx2_den_bu["Sku Quantity of return"].sum()

    COMBO_SCx1_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "COMBO-SCX1")
    ]

    COMBO_SCx2_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "COMBO-SCX2")
    ]

    so_luong_COMBO_SCx1_hoan_tra = COMBO_SCx1_hoan_tra["Sku Quantity of return"].sum()
    so_luong_COMBO_SCx2_hoan_tra = COMBO_SCx2_hoan_tra["Sku Quantity of return"].sum()

    SC_X1_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "COMBO-SCX1")
    ]

    SC_X2_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "COMBO-SCX2")
    ]

    so_luong_COMBO_SCx1_boom = SC_X1_boom["Quantity"].sum()
    so_luong_COMBO_SCx2_boom = SC_X2_boom["Quantity"].sum()

    # BÁNH TRÁNG
    # BTHP-0CAY, BTHP-CAY, BTHP-COMBO, BTHP-COMBO-0CAY, BTHP-COMBO-CAY
    BTHP_0CAY_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "BTHP-0CAY") & (df_merged["Total revenue"] > 0)
    ]

    BTHP_CAY_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "BTHP-CAY") & (df_merged["Total revenue"] > 0)
    ]

    BTHP_COMBO_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "BTHP-COMBO") & (df_merged["Total revenue"] > 0)
    ]

    BTHP_COMBO_0CAY_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "BTHP-COMBO-0CAY")
        & (df_merged["Total revenue"] > 0)
    ]

    BTHP_COMBO_CAY_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "BTHP-COMBO-CAY")
        & (df_merged["Total revenue"] > 0)
    ]

    so_luong_BTHP_0CAY_hoan_thanh = BTHP_0CAY_hoan_thanh["Quantity"].sum()
    so_luong_BTHP_CAY_hoan_thanh = BTHP_CAY_hoan_thanh["Quantity"].sum()
    so_luong_BTHP_COMBO_hoan_thanh = BTHP_COMBO_hoan_thanh["Quantity"].sum()
    so_luong_BTHP_COMBO_0CAY_hoan_thanh = BTHP_COMBO_0CAY_hoan_thanh["Quantity"].sum()
    so_luong_BTHP_COMBO_CAY_hoan_thanh = BTHP_COMBO_CAY_hoan_thanh["Quantity"].sum()

    BTHP_0CAY_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "BTHP-0CAY")
        )
    ]

    BTHP_CAY_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "BTHP-CAY")
        )
    ]

    BTHP_COMBO_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "BTHP-COMBO")
        )
    ]

    BTHP_COMBO_0CAY_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "BTHP-COMBO-0CAY")
        )
    ]

    BTHP_COMBO_CAY_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "BTHP-COMBO-CAY")
        )
    ]

    so_luong_BTHP_0CAY_den_bu = BTHP_0CAY_den_bu["Sku Quantity of return"].sum()
    so_luong_BTHP_CAY_den_bu = BTHP_CAY_den_bu["Sku Quantity of return"].sum()
    so_luong_BTHP_COMBO_den_bu = BTHP_COMBO_den_bu["Sku Quantity of return"].sum()
    so_luong_BTHP_COMBO_0CAY_den_bu = BTHP_COMBO_0CAY_den_bu[
        "Sku Quantity of return"
    ].sum()
    so_luong_BTHP_COMBO_CAY_den_bu = BTHP_COMBO_CAY_den_bu[
        "Sku Quantity of return"
    ].sum()

    BTHP_0CAY_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "BTHP-0CAY")
    ]

    BTHP_CAY_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "BTHP-CAY")
    ]

    BTHP_COMBO_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "BTHP-COMBO")
    ]

    BTHP_COMBO_0CAY_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "BTHP-COMBO-0CAY")
    ]

    BTHP_COMBO_CAY_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "BTHP-COMBO-CAY")
    ]

    so_luong_BTHP_0CAY_hoan_tra = BTHP_0CAY_hoan_tra["Sku Quantity of return"].sum()
    so_luong_BTHP_CAY_hoan_tra = BTHP_CAY_hoan_tra["Sku Quantity of return"].sum()
    so_luong_BTHP_COMBO_hoan_tra = BTHP_COMBO_hoan_tra["Sku Quantity of return"].sum()
    so_luong_BTHP_COMBO_0CAY_hoan_tra = BTHP_COMBO_0CAY_hoan_tra[
        "Sku Quantity of return"
    ].sum()
    so_luong_BTHP_COMBO_CAY_hoan_tra = BTHP_COMBO_CAY_hoan_tra[
        "Sku Quantity of return"
    ].sum()

    BTHP_0CAY_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "BTHP-0CAY")
    ]

    BTHP_CAY_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "BTHP-CAY")
    ]

    BTHP_COMBO_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "BTHP-COMBO")
    ]

    BTHP_COMBO_0CAY_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "BTHP-COMBO-0CAY")
    ]

    BTHP_COMBO_CAY_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "BTHP-COMBO-CAY")
    ]

    so_luong_BTHP_0CAY_boom = BTHP_0CAY_boom["Quantity"].sum()
    so_luong_BTHP_CAY_boom = BTHP_CAY_boom["Quantity"].sum()
    so_luong_BTHP_COMBO_boom = BTHP_COMBO_boom["Quantity"].sum()
    so_luong_BTHP_COMBO_0CAY_boom = BTHP_COMBO_0CAY_boom["Quantity"].sum()
    so_luong_BTHP_COMBO_CAY_boom = BTHP_COMBO_CAY_boom["Quantity"].sum()

    # COMBO new

    COMBO_BTHP_SCx1_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "COMBO_BTHP_SCx1")
        & (df_merged["Total revenue"] > 0)
    ]

    COMBO_BTHP_SCx2_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "COMBO_BTHP_SCx2")
        & (df_merged["Total revenue"] > 0)
    ]

    COMBO_BTHP_SCx1_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "COMBO_BTHP_SCx1")
        )
    ]

    COMBO_BTHP_SCx2_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "COMBO_BTHP_SCx2")
        )
    ]

    COMBO_BTHP_SCx1_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "COMBO_BTHP_SCx1")
    ]

    COMBO_BTHP_SCx2_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "COMBO_BTHP_SCx2")
    ]

    COMBO_BTHP_SCx1_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "COMBO_BTHP_SCx1")
    ]

    COMBO_BTHP_SCx2_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "COMBO_BTHP_SCx2")
    ]

    soluong_COMBO_BTHP_SCx1_hoan_thanh = COMBO_BTHP_SCx1_hoan_thanh["Quantity"].sum()
    soluong_COMBO_BTHP_SCx2_hoan_thanh = COMBO_BTHP_SCx2_hoan_thanh["Quantity"].sum()
    soluong_COMBO_BTHP_SCx1_den_bu = COMBO_BTHP_SCx1_den_bu["Quantity"].sum()
    soluong_COMBO_BTHP_SCx2_den_bu = COMBO_BTHP_SCx2_den_bu["Quantity"].sum()
    soluong_COMBO_BTHP_SCx1_hoan_tra = COMBO_BTHP_SCx1_hoan_tra["Quantity"].sum()
    soluong_COMBO_BTHP_SCx2_hoan_tra = COMBO_BTHP_SCx2_hoan_tra["Quantity"].sum()
    soluong_COMBO_BTHP_SCx1_boom = COMBO_BTHP_SCx1_boom["Quantity"].sum()
    soluong_COMBO_BTHP_SCx2_boom = COMBO_BTHP_SCx2_boom["Quantity"].sum()

    COMBO_4BTHP_hoan_thanh = df_merged[
        (df_merged["SKU Category"] == "COMBO_4BTHP") & (df_merged["Total revenue"] > 0)
    ]

    COMBO_4BTHP_den_bu = df_merged[
        (
            df_merged["Type"].isin(
                ["Logistics reimbursement", "Platform reimbursement"]
            )
            & (df_merged["SKU Category"] == "COMBO_4BTHP")
        )
    ]

    COMBO_4BTHP_hoan_tra = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["Sku Quantity of return"] != 0)
        & (df_merged["Cancelation/Return Type"].isin(["Return/Refund", ""]))
        & (df_merged["Classify"] == "Not Duplicate")
        & (df_merged["SKU Category"] == "COMBO_4BTHP")
    ]

    COMBO_4BTHP_boom = df_merged[
        (df_merged["Type"] == "Order")
        & (df_merged["Cancelation/Return Type"] == "Cancel")
        & (df_merged["Total revenue"] <= 0)
        & (df_merged["SKU Category"] == "COMBO_4BTHP")
    ]

    soluong_COMBO_4BTHP_hoan_thanh = COMBO_4BTHP_hoan_thanh["Quantity"].sum()
    soluong_COMBO_4BTHP_den_bu = COMBO_4BTHP_den_bu["Quantity"].sum()
    soluong_COMBO_4BTHP_hoan_tra = COMBO_4BTHP_hoan_tra["Quantity"].sum()
    soluong_COMBO_4BTHP_boom = COMBO_4BTHP_boom["Quantity"].sum()

    # Tính toán tổng số lượng sản phẩm hoàn thành và quyết toán
    so_luong_SCx1_tiktok_quyet_toan = (
        so_luong_SCx1_tiktok_hoan_thanh
        + So_luong_SC_X1_den_bu
        + so_luong_COMBO_SCx1_hoan_thanh * 2
        + so_luong_COMBO_SCx1_den_bu * 2
    )
    so_luong_SCx2_tiktok_quyet_toan = (
        so_luong_SCx2_tiktok_hoan_thanh
        + So_luong_SC_X2_den_bu
        + so_luong_COMBO_SCx2_hoan_thanh * 2
        + so_luong_COMBO_SCx2_den_bu * 2
    )
    so_luong_SCxCombo_tiktok_quyet_toan = (
        so_luong_SC_combo_tiktok_hoan_thanh * 2 + So_luong_SC_Combo_den_bu * 2
    )

    Tong_BTHP_hoan_ve = (
        so_luong_BTHP_0CAY_boom
        + so_luong_BTHP_CAY_boom
        + so_luong_BTHP_COMBO_boom * 2
        + so_luong_BTHP_COMBO_0CAY_boom * 2
        + so_luong_BTHP_COMBO_CAY_boom * 2
        + so_luong_BTHP_0CAY_hoan_tra
        + so_luong_BTHP_CAY_hoan_tra
        + so_luong_BTHP_COMBO_hoan_tra * 2
        + so_luong_BTHP_COMBO_0CAY_hoan_tra * 2
        + so_luong_BTHP_COMBO_CAY_hoan_tra * 2
    )

    Tong_von_SC = (
        so_luong_SCx1_tiktok_quyet_toan * VonX1
        + so_luong_SCx2_tiktok_quyet_toan * VonX2
        + so_luong_SCxCombo_tiktok_quyet_toan * VonCombo
    )

    Tong_von_BTHP = (
        (so_luong_BTHP_0CAY_hoan_thanh + so_luong_BTHP_0CAY_den_bu) * VonBTHP_0CAY
        + (so_luong_BTHP_CAY_hoan_thanh + so_luong_BTHP_CAY_den_bu) * VonBTHP_CAY
        + (so_luong_BTHP_COMBO_hoan_thanh + so_luong_BTHP_COMBO_den_bu) * VonBTHP_COMBO
    )

    return (
        soluong_COMBO_4BTHP_hoan_thanh,
        soluong_COMBO_4BTHP_den_bu,
        soluong_COMBO_4BTHP_hoan_tra,
        soluong_COMBO_4BTHP_boom,
        ###
        soluong_COMBO_BTHP_SCx1_hoan_thanh,
        soluong_COMBO_BTHP_SCx2_hoan_thanh,
        soluong_COMBO_BTHP_SCx1_den_bu,
        soluong_COMBO_BTHP_SCx2_den_bu,
        soluong_COMBO_BTHP_SCx1_hoan_tra,
        soluong_COMBO_BTHP_SCx2_hoan_tra,
        soluong_COMBO_BTHP_SCx1_boom,
        soluong_COMBO_BTHP_SCx2_boom,
        # BÁNH TRÁNG
        so_luong_BTHP_COMBO_0CAY_hoan_thanh,
        so_luong_BTHP_COMBO_CAY_hoan_thanh,
        so_luong_BTHP_COMBO_0CAY_den_bu,
        so_luong_BTHP_COMBO_CAY_den_bu,
        so_luong_BTHP_COMBO_0CAY_hoan_tra,
        so_luong_BTHP_COMBO_CAY_hoan_tra,
        so_luong_BTHP_COMBO_0CAY_boom,
        so_luong_BTHP_COMBO_CAY_boom,
        so_luong_BTHP_0CAY_hoan_thanh,
        so_luong_BTHP_CAY_hoan_thanh,
        so_luong_BTHP_COMBO_hoan_thanh,
        so_luong_BTHP_0CAY_den_bu,
        so_luong_BTHP_CAY_den_bu,
        so_luong_BTHP_COMBO_den_bu,
        so_luong_BTHP_0CAY_hoan_tra,
        so_luong_BTHP_CAY_hoan_tra,
        so_luong_BTHP_COMBO_hoan_tra,
        so_luong_BTHP_0CAY_boom,
        so_luong_BTHP_CAY_boom,
        so_luong_BTHP_COMBO_boom,
        # SC và COMBO mới
        so_luong_COMBO_SCx1_hoan_thanh,
        so_luong_COMBO_SCx2_hoan_thanh,
        so_luong_COMBO_SCx1_den_bu,
        so_luong_COMBO_SCx2_den_bu,
        so_luong_COMBO_SCx1_hoan_tra,
        so_luong_COMBO_SCx2_hoan_tra,
        so_luong_COMBO_SCx1_boom,
        so_luong_COMBO_SCx2_boom,
        So_luong_SC_X1_den_bu,
        So_luong_SC_X2_den_bu,
        So_luong_SC_Combo_den_bu,
        So_luong_SC_X1_hoan_tra,
        So_luong_SC_X2_hoan_tra,
        So_luong_SC_combo_hoan_tra,
        So_luong_SC_X1_boom,
        So_luong_SC_X2_boom,
        So_luong_SC_combo_boom,
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
        Tong_tien_quyet_toan,
        Tong_tien_hoan_thanh,
        Tong_phi,
        Tong_von_SC,
        Tong_von_BTHP,
        Tong_BTHP_hoan_ve,
    )


import streamlit as st
from PIL import Image
import base64

# 🔺 Đặt lệnh set_page_config ở dòng đầu tiên
st.set_page_config(page_title="REPORT DAILY OF TIKTOK", layout="wide")


# Chèn logo từ GitHub vào góc trên bên trái
st.markdown(
    """
    <div style='top: 60px; left: 40px; z-index: 1000;'>
        <img src='https://raw.githubusercontent.com/CaptainCattt/Report_of_shopee/main/logo-lamvlog.png' width='150'/>
    </div>
    """,
    unsafe_allow_html=True,
)

# ======= TIÊU ĐỀ CĂN GIỮA =======
st.markdown(
    """
    <div style='text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px;'>
        <img src='https://img.icons8.com/?size=100&id=118638&format=png&color=000000' width='40'/>
        <h1 style='color: black; margin: 0;'>REPORT DAILY OF TIKTOK</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br><br><br>", unsafe_allow_html=True)


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
                soluong_COMBO_4BTHP_hoan_thanh,
                soluong_COMBO_4BTHP_den_bu,
                soluong_COMBO_4BTHP_hoan_tra,
                soluong_COMBO_4BTHP_boom,
                ###
                soluong_COMBO_BTHP_SCx1_hoan_thanh,
                soluong_COMBO_BTHP_SCx2_hoan_thanh,
                soluong_COMBO_BTHP_SCx1_den_bu,
                soluong_COMBO_BTHP_SCx2_den_bu,
                soluong_COMBO_BTHP_SCx1_hoan_tra,
                soluong_COMBO_BTHP_SCx2_hoan_tra,
                soluong_COMBO_BTHP_SCx1_boom,
                soluong_COMBO_BTHP_SCx2_boom,
                # BÁNH TRÁNG
                so_luong_BTHP_COMBO_0CAY_hoan_thanh,
                so_luong_BTHP_COMBO_CAY_hoan_thanh,
                so_luong_BTHP_COMBO_0CAY_den_bu,
                so_luong_BTHP_COMBO_CAY_den_bu,
                so_luong_BTHP_COMBO_0CAY_hoan_tra,
                so_luong_BTHP_COMBO_CAY_hoan_tra,
                so_luong_BTHP_COMBO_0CAY_boom,
                so_luong_BTHP_COMBO_CAY_boom,
                so_luong_BTHP_0CAY_hoan_thanh,
                so_luong_BTHP_CAY_hoan_thanh,
                so_luong_BTHP_COMBO_hoan_thanh,
                so_luong_BTHP_0CAY_den_bu,
                so_luong_BTHP_CAY_den_bu,
                so_luong_BTHP_COMBO_den_bu,
                so_luong_BTHP_0CAY_hoan_tra,
                so_luong_BTHP_CAY_hoan_tra,
                so_luong_BTHP_COMBO_hoan_tra,
                so_luong_BTHP_0CAY_boom,
                so_luong_BTHP_CAY_boom,
                so_luong_BTHP_COMBO_boom,
                # SC và COMBO mới
                so_luong_COMBO_SCx1_hoan_thanh,
                so_luong_COMBO_SCx2_hoan_thanh,
                so_luong_COMBO_SCx1_den_bu,
                so_luong_COMBO_SCx2_den_bu,
                so_luong_COMBO_SCx1_hoan_tra,
                so_luong_COMBO_SCx2_hoan_tra,
                so_luong_COMBO_SCx1_boom,
                so_luong_COMBO_SCx2_boom,
                So_luong_SC_X1_den_bu,
                So_luong_SC_X2_den_bu,
                So_luong_SC_Combo_den_bu,
                So_luong_SC_X1_hoan_tra,
                So_luong_SC_X2_hoan_tra,
                So_luong_SC_combo_hoan_tra,
                So_luong_SC_X1_boom,
                So_luong_SC_X2_boom,
                So_luong_SC_combo_boom,
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
                Tong_tien_quyet_toan,
                Tong_tien_hoan_thanh,
                Tong_phi,
                Tong_von_SC,
                Tong_von_BTHP,
                Tong_BTHP_hoan_ve,
            ) = process_tiktok_daily_report(df_all, df_income)

            st.session_state["Don_quyet_toan"] = Don_quyet_toan
            st.session_state["Don_hoan_thanh"] = Don_hoan_thanh
            st.session_state["Don_thanh_toan_truoc"] = Don_thanh_toan_truoc
            st.session_state["Don_boom"] = Don_boom
            st.session_state["Don_hoan_tra"] = Don_hoan_tra
            st.session_state["Don_dieu_chinh_tru_phi"] = Don_dieu_chinh_tru_phi
            st.session_state["Don_dieu_chinh_san_den_bu"] = Don_dieu_chinh_san_den_bu
            st.session_state["Don_dieu_chinh"] = Don_dieu_chinh
            st.session_state["Tong_tien_quyet_toan"] = Tong_tien_quyet_toan
            st.session_state["Tong_tien_hoan_thanh"] = Tong_tien_hoan_thanh

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

            bang_thong_ke_tien_tiktok = pd.DataFrame(
                {
                    "SỐ TIỀN QUYẾT TOÁN": [Tong_tien_quyet_toan],
                    "SỐ TIỀN HOÀN THÀNH": [Tong_tien_hoan_thanh],
                    "PHÍ": [Tong_phi],
                    "TỔNG VỐN SỐT CHẤM": [Tong_von_SC],
                    "TỔNG VỐN BÁNH TRÁNG": [Tong_von_BTHP],
                    "TỔNG VỐN": [Tong_von_SC + Tong_von_BTHP],
                    "LỢI NHUẬN": [Tong_tien_quyet_toan - Tong_von_SC],
                },
                index=["Tiktok"],
            )

            bang_thong_ke_so_luong_tiktok = pd.DataFrame(
                {
                    "TỔNG SỐ LƯỢNG SC": [
                        (
                            so_luong_SCx1_tiktok_hoan_thanh
                            + so_luong_SCx2_tiktok_hoan_thanh
                            + so_luong_SC_combo_tiktok_hoan_thanh * 2
                            + so_luong_COMBO_SCx1_hoan_thanh * 2
                            + so_luong_COMBO_SCx2_hoan_thanh * 2
                        ),
                        (
                            so_luong_SCx1_tiktok_hoan_thanh
                            + So_luong_SC_X1_den_bu
                            + so_luong_COMBO_SCx1_hoan_thanh * 2
                            + so_luong_COMBO_SCx1_den_bu * 2
                            + so_luong_SCx2_tiktok_hoan_thanh
                            + So_luong_SC_X2_den_bu
                            + so_luong_COMBO_SCx2_hoan_thanh * 2
                            + so_luong_COMBO_SCx2_den_bu * 2
                            + so_luong_SC_combo_tiktok_hoan_thanh * 2
                            + So_luong_SC_Combo_den_bu * 2
                        ),
                        (
                            So_luong_SC_X1_boom
                            + So_luong_SC_X1_hoan_tra
                            + so_luong_COMBO_SCx1_boom * 2
                            + so_luong_COMBO_SCx1_hoan_tra * 2
                            + So_luong_SC_X2_boom
                            + So_luong_SC_X2_hoan_tra
                            + so_luong_COMBO_SCx2_boom * 2
                            + so_luong_COMBO_SCx2_hoan_tra * 2
                            + So_luong_SC_combo_boom * 2
                            + So_luong_SC_combo_hoan_tra * 2
                        ),
                    ],
                    "SCx1": [
                        so_luong_SCx1_tiktok_hoan_thanh,
                        so_luong_SCx1_tiktok_hoan_thanh + So_luong_SC_X1_den_bu,
                        So_luong_SC_X1_boom + So_luong_SC_X1_hoan_tra,
                    ],
                    "SCx2": [
                        so_luong_SCx2_tiktok_hoan_thanh,
                        so_luong_SCx2_tiktok_hoan_thanh + So_luong_SC_X2_den_bu,
                        So_luong_SC_X2_boom + So_luong_SC_X2_hoan_tra,
                    ],
                    "SCxCOMBO": [
                        so_luong_SC_combo_tiktok_hoan_thanh,
                        so_luong_SC_combo_tiktok_hoan_thanh + So_luong_SC_Combo_den_bu,
                        So_luong_SC_combo_boom + So_luong_SC_combo_hoan_tra,
                    ],
                    "COMBO_SCx1": [
                        so_luong_COMBO_SCx1_hoan_thanh,
                        so_luong_COMBO_SCx1_hoan_thanh + so_luong_COMBO_SCx1_den_bu,
                        so_luong_COMBO_SCx1_boom + so_luong_COMBO_SCx1_hoan_tra,
                    ],
                    "COMBO_SCx2": [
                        so_luong_COMBO_SCx2_hoan_thanh,
                        so_luong_COMBO_SCx2_hoan_thanh + so_luong_COMBO_SCx2_den_bu,
                        so_luong_COMBO_SCx2_boom + so_luong_COMBO_SCx2_hoan_tra,
                    ],
                },
                index=["HOÀN THÀNH", "QUYẾT TOÁN", "HOÀN VỀ"],
            )

            bang_thong_ke_so_luong_BTHP_tiktok = pd.DataFrame(
                {
                    "TỔNG SỐ LƯỢNG BTHP": [
                        # HOÀN THÀNH
                        (
                            so_luong_BTHP_0CAY_hoan_thanh
                            + so_luong_BTHP_CAY_hoan_thanh
                            + so_luong_BTHP_COMBO_hoan_thanh * 2
                            + so_luong_BTHP_COMBO_0CAY_hoan_thanh * 2
                            + so_luong_BTHP_COMBO_CAY_hoan_thanh * 2
                            + soluong_COMBO_BTHP_SCx1_hoan_thanh * 2
                            + soluong_COMBO_BTHP_SCx2_hoan_thanh * 2
                            + soluong_COMBO_4BTHP_hoan_thanh * 4
                        ),
                        # QUYẾT TOÁN
                        (
                            so_luong_BTHP_0CAY_hoan_thanh
                            + so_luong_BTHP_CAY_hoan_thanh
                            + so_luong_BTHP_COMBO_hoan_thanh * 2
                            + so_luong_BTHP_COMBO_0CAY_hoan_thanh * 2
                            + so_luong_BTHP_COMBO_CAY_hoan_thanh * 2
                            + soluong_COMBO_BTHP_SCx1_hoan_thanh * 2
                            + soluong_COMBO_BTHP_SCx2_hoan_thanh * 2
                            + soluong_COMBO_4BTHP_hoan_thanh * 4
                            + so_luong_BTHP_0CAY_den_bu
                            + so_luong_BTHP_CAY_den_bu
                            + so_luong_BTHP_COMBO_den_bu * 2
                            + so_luong_BTHP_COMBO_0CAY_den_bu * 2
                            + so_luong_BTHP_COMBO_CAY_den_bu * 2
                            + soluong_COMBO_BTHP_SCx1_den_bu * 2
                            + soluong_COMBO_BTHP_SCx2_den_bu * 2
                            + soluong_COMBO_4BTHP_den_bu * 4
                        ),
                        # HOÀN VỀ
                        (
                            so_luong_BTHP_0CAY_boom
                            + so_luong_BTHP_CAY_boom
                            + so_luong_BTHP_COMBO_boom * 2
                            + so_luong_BTHP_COMBO_0CAY_boom * 2
                            + so_luong_BTHP_COMBO_CAY_boom * 2
                            + soluong_COMBO_BTHP_SCx1_boom * 2
                            + soluong_COMBO_BTHP_SCx2_boom * 2
                            + soluong_COMBO_4BTHP_boom * 4
                            + so_luong_BTHP_0CAY_hoan_tra
                            + so_luong_BTHP_CAY_hoan_tra
                            + so_luong_BTHP_COMBO_hoan_tra * 2
                            + so_luong_BTHP_COMBO_0CAY_hoan_tra * 2
                            + so_luong_BTHP_COMBO_CAY_hoan_tra * 2
                            + soluong_COMBO_BTHP_SCx1_hoan_tra * 2
                            + soluong_COMBO_BTHP_SCx2_hoan_tra * 2
                            + soluong_COMBO_4BTHP_hoan_tra * 4
                        ),
                    ],
                    "BTHP_0CAY": [
                        so_luong_BTHP_0CAY_hoan_thanh,
                        so_luong_BTHP_0CAY_hoan_thanh + so_luong_BTHP_0CAY_den_bu,
                        so_luong_BTHP_0CAY_boom + so_luong_BTHP_0CAY_hoan_tra,
                    ],
                    "BTHP_CAY": [
                        so_luong_BTHP_CAY_hoan_thanh,
                        so_luong_BTHP_CAY_hoan_thanh + so_luong_BTHP_CAY_den_bu,
                        so_luong_BTHP_CAY_boom + so_luong_BTHP_CAY_hoan_tra,
                    ],
                    "BTHP_COMBO": [
                        so_luong_BTHP_COMBO_hoan_thanh,
                        so_luong_BTHP_COMBO_hoan_thanh + so_luong_BTHP_COMBO_den_bu,
                        so_luong_BTHP_COMBO_boom + so_luong_BTHP_COMBO_hoan_tra,
                    ],
                    "BTHP_COMBO_0CAY": [
                        so_luong_BTHP_COMBO_0CAY_hoan_thanh,
                        so_luong_BTHP_COMBO_0CAY_hoan_thanh
                        + so_luong_BTHP_COMBO_0CAY_den_bu,
                        so_luong_BTHP_COMBO_0CAY_boom
                        + so_luong_BTHP_COMBO_0CAY_hoan_tra,
                    ],
                    "BTHP_COMBO_CAY": [
                        so_luong_BTHP_COMBO_CAY_hoan_thanh,
                        so_luong_BTHP_COMBO_CAY_hoan_thanh
                        + so_luong_BTHP_COMBO_CAY_den_bu,
                        so_luong_BTHP_COMBO_CAY_boom + so_luong_BTHP_COMBO_CAY_hoan_tra,
                    ],
                    "COMBO_BTHP + SCx1": [
                        soluong_COMBO_BTHP_SCx1_hoan_thanh,
                        soluong_COMBO_BTHP_SCx1_hoan_thanh
                        + soluong_COMBO_BTHP_SCx1_den_bu,
                        soluong_COMBO_BTHP_SCx1_boom + soluong_COMBO_BTHP_SCx1_hoan_tra,
                    ],
                    "COMBO_BTHP + SCx2": [
                        soluong_COMBO_BTHP_SCx2_hoan_thanh,
                        soluong_COMBO_BTHP_SCx2_hoan_thanh
                        + soluong_COMBO_BTHP_SCx2_den_bu,
                        soluong_COMBO_BTHP_SCx2_boom + soluong_COMBO_BTHP_SCx2_hoan_tra,
                    ],
                    "COMBO_4_BTHP": [
                        soluong_COMBO_4BTHP_hoan_thanh,
                        soluong_COMBO_4BTHP_hoan_thanh + soluong_COMBO_4BTHP_den_bu,
                        soluong_COMBO_4BTHP_boom + soluong_COMBO_4BTHP_hoan_tra,
                    ],
                },
                index=["HOÀN THÀNH", "QUYẾT TOÁN", "HOÀN VỀ"],
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
            # Gán màu riêng cho "ĐƠN QUYẾT TOÁN"
            color_map = {"ĐƠN QUYẾT TOÁN": "green"}
            # Biểu đồ cột
            fig_bar_tiktok = px.bar(
                df_bar,
                x="Loại đơn hàng",
                y="Số lượng",
                color="Loại đơn hàng",
                color_discrete_map=color_map,
                title="Số lượng các loại đơn hàng TikTok",
                text_auto=True,
                labels={"Loại đơn hàng": "Loại đơn", "Số lượng": "Số đơn"},
            )

            # Biểu đồ tròn Quyết Toán
            fig_pie_quyet_toan_bthp = px.pie(
                names=[
                    "BTHP Không Cay",
                    "BTHP Cay",
                    "BTHP COMBO",
                    "COMBO Không Cay",
                    "COMBO Cay",
                ],
                values=[
                    so_luong_BTHP_0CAY_hoan_thanh + so_luong_BTHP_CAY_den_bu,
                    so_luong_BTHP_CAY_hoan_thanh + so_luong_BTHP_CAY_den_bu,
                    so_luong_BTHP_COMBO_hoan_thanh + so_luong_BTHP_COMBO_den_bu,
                    so_luong_BTHP_COMBO_0CAY_hoan_thanh
                    + so_luong_BTHP_COMBO_0CAY_den_bu,
                    so_luong_BTHP_COMBO_CAY_hoan_thanh + so_luong_BTHP_COMBO_CAY_den_bu,
                ],
                title="Tỉ lệ sản phẩm HOÀN THÀNH TikTok",
                hole=0.4,
            )

            # Biểu đồ tròn Quyết Toán
            fig_pie_quyet_toan_sc = px.pie(
                names=["SCx1", "SCx2", "SC COMBO", "COMBO X1", "COMBO X2"],
                values=[
                    so_luong_SCx1_tiktok_quyet_toan,
                    so_luong_SCx2_tiktok_quyet_toan,
                    so_luong_SCxCombo_tiktok_quyet_toan,
                    so_luong_COMBO_SCx1_hoan_thanh + so_luong_COMBO_SCx1_den_bu,
                    so_luong_COMBO_SCx2_hoan_thanh + so_luong_COMBO_SCx2_den_bu,
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
            st.session_state["bang_thong_ke_so_luong_BTHP_tiktok"] = (
                bang_thong_ke_so_luong_BTHP_tiktok
            )
            st.session_state["bang_thong_ke_tien_tiktok"] = bang_thong_ke_tien_tiktok
            st.session_state["fig_bar_tiktok"] = fig_bar_tiktok
            st.session_state["fig_pie_quyet_toan_bthp"] = fig_pie_quyet_toan_bthp
            st.session_state["fig_pie_quyet_toan_sc"] = fig_pie_quyet_toan_sc
            st.session_state.processing = True

# --- Hiển thị kết quả nếu đã xử lý ---
if st.session_state.processing:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='text-align: center; color: #FF9800;'>📊 KẾT QUẢ THỐNG KÊ</h3>",
        unsafe_allow_html=True,
    )
    st.markdown("<br><br>", unsafe_allow_html=True)

    with st.container():
        st.markdown("#### 📋 Bảng Thống Kê Tiền Hàng")
        st.dataframe(st.session_state["bang_thong_ke_tien_tiktok"])

    with st.container():
        st.markdown("#### 📋 Bảng Thống Kê Đơn Hàng")
        st.dataframe(st.session_state["bang_thong_ke_don_hang_tiktok"])

    st.markdown("#### 📈 Biểu Đồ Số Lượng Đơn Hàng")
    st.plotly_chart(st.session_state["fig_bar_tiktok"], use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 📋 Bảng Thống Kê Sản Phẩm SỐT CHẤM")
        st.dataframe(st.session_state["bang_thong_ke_so_luong_tiktok"])

    with col4:
        st.markdown("#### 📋 Bảng Thống Kê Sản Phẩm BÁNH TRÁNG HÀNH PHI")
        st.dataframe(st.session_state["bang_thong_ke_so_luong_BTHP_tiktok"])

    # Hiển thị thống kê sản phẩm
    st.markdown("### 📊 SỐ LƯỢNG SẢN PHẨM")
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("#### 📈 Biểu Đồ Quyết Toán Sốt Chấm")
        st.plotly_chart(
            st.session_state["fig_pie_quyet_toan_sc"], use_container_width=True
        )

    with col6:
        st.markdown("#### 📈 Biểu Đồ Quyết Toán Bánh Tráng Hành Phi")
        st.plotly_chart(
            st.session_state["fig_pie_quyet_toan_bthp"], use_container_width=True
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


df_chi_tiet = mapping.get(loai_don, pd.DataFrame())

# Hiển thị kết quả
if not df_chi_tiet.empty:
    st.markdown(f"#### 📋 Danh sách chi tiết {loai_don}")
    st.dataframe(df_chi_tiet)
else:
    st.info("Không có dữ liệu cho loại đơn này.")
