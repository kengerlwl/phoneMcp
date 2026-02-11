"""App name to package name mapping for supported applications."""

APP_PACKAGES: dict[str, str] = {
    # Social & Messaging
    "微信": "com.tencent.mm",
    "WeChat": "com.tencent.mm",
    "QQ": "com.tencent.mobileqq",
    "微博": "com.sina.weibo",
    "Telegram": "org.telegram.messenger",
    "WhatsApp": "com.whatsapp",
    # E-commerce
    "淘宝": "com.taobao.taobao",
    "京东": "com.jingdong.app.mall",
    "拼多多": "com.xunmeng.pinduoduo",
    "Temu": "com.einnovation.temu",
    # Lifestyle & Social
    "小红书": "com.xingin.xhs",
    "豆瓣": "com.douban.frodo",
    "知乎": "com.zhihu.android",
    "Reddit": "com.reddit.frontpage",
    # Maps & Navigation
    "高德地图": "com.autonavi.minimap",
    "百度地图": "com.baidu.BaiduMap",
    "Google Maps": "com.google.android.apps.maps",
    # Food & Services
    "美团": "com.sankuai.meituan",
    "大众点评": "com.dianping.v1",
    "饿了么": "me.ele",
    # Travel
    "携程": "ctrip.android.view",
    "12306": "com.MobileTicket",
    "滴滴出行": "com.sdu.didi.psnger",
    "Booking": "com.booking",
    "Expedia": "com.expedia.bookings",
    # Video & Entertainment
    "bilibili": "tv.danmaku.bili",
    "抖音": "com.ss.android.ugc.aweme",
    "TikTok": "com.zhiliaoapp.musically",
    "快手": "com.smile.gifmaker",
    "腾讯视频": "com.tencent.qqlive",
    "爱奇艺": "com.qiyi.video",
    "优酷视频": "com.youku.phone",
    # Music & Audio
    "网易云音乐": "com.netease.cloudmusic",
    "QQ音乐": "com.tencent.qqmusic",
    "喜马拉雅": "com.ximalaya.ting.android",
    # Reading
    "番茄小说": "com.dragon.read",
    # Productivity
    "飞书": "com.ss.android.lark",
    "Gmail": "com.google.android.gm",
    "Google Drive": "com.google.android.apps.docs",
    "Google Calendar": "com.google.android.calendar",
    # AI & Tools
    "豆包": "com.larus.nova",
    # System
    "Settings": "com.android.settings",
    "Chrome": "com.android.chrome",
    "Clock": "com.android.deskclock",
    "Contacts": "com.android.contacts",
    "Files": "com.android.fileexplorer",
    "Google Play Store": "com.android.vending",
}


def get_package_name(app_name: str) -> str | None:
    """Get the package name for an app."""
    return APP_PACKAGES.get(app_name)


def get_app_name(package_name: str) -> str | None:
    """Get the app name from a package name."""
    for name, package in APP_PACKAGES.items():
        if package == package_name:
            return name
    return None


def list_supported_apps() -> list[str]:
    """Get a list of all supported app names."""
    return list(APP_PACKAGES.keys())

