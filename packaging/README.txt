Risk of Rain 2 — التعريب العربي / Arabic translation
================================================================

ما هذا / What this is
----------------------------------------------------------------
تعريب لـ Risk of Rain 2 على هيئة إضافة (plugin) تعمل عبر BepInEx:
القوائم والإعدادات والناجون ومهاراتهم والأغراض والعتاد والمُسيّرات
والوحوش والأطوار والإنجازات والسجلّ وحوارات الزعماء.
لا يُعدَّل أي ملف من ملفات اللعبة: كل شيء داخل
BepInEx/plugins/RoR2Arabic، وحذفه يعيد اللعبة كما كانت تمامًا.

An Arabic translation of Risk of Rain 2, delivered as a BepInEx
plugin. No game file is modified - everything lives in
BepInEx/plugins/RoR2Arabic and deleting it puts the game back as it
was.


المتطلبات / Requirements
----------------------------------------------------------------
- ويندوز 10 أو 11، أو أي توزيعة لينكس حديثة.
- اللعبة من Steam.
- BepInEx 5.4.21 (نسخة x64) في مجلد اللعبة.

- Windows 10/11 or any modern Linux.
- The Steam version of the game.
- BepInEx 5.4.21 (x64) inside the game folder.


قبل التثبيت / Before you install
----------------------------------------------------------------
1. نزّل BepInEx 5.4.21 (نسخة x64) من
   https://github.com/BepInEx/BepInEx/releases
2. فُكّ ضغطه داخل مجلد اللعبة، بحيث يصير مجلد BepInEx بجوار
   Risk of Rain 2.exe.
3. شغّل اللعبة مرة واحدة ثم أغلقها.

إن كنت تستعمل r2modman أو Thunderstore Mod Manager فإن BepInEx
موجود مسبقًا داخل مجلد الملف الشخصي (profile)، ووجّه المثبّت
إلى ذلك المجلد.

1. Download BepInEx 5.4.21 (x64) from the releases page above.
2. Unzip it into the game folder so BepInEx/ sits next to
   Risk of Rain 2.exe.
3. Run the game once, then close it.

If you use r2modman or Thunderstore Mod Manager, BepInEx is already
inside the profile folder - point the installer there.


التثبيت على ويندوز / Installing on Windows
----------------------------------------------------------------
1. أغلق اللعبة.
2. انقر نقرًا مزدوجًا على install-windows.bat.
3. اضغط "تثبيت". سيبحث المثبّت عن اللعبة وحده؛ إن لم يجدها اضغط
   "استعراض..." وحدّد المجلد الذي يحتوي على Risk of Rain 2.exe.
وإن ظهرت رسالة عن الصلاحيات، شغّل الملف بزر الفأرة الأيمن ثم
"تشغيل كمسؤول".

1. Close the game.
2. Double-click install-windows.bat.
3. Press Install. It finds the game by itself; if it cannot, press
   Browse and pick the folder that has Risk of Rain 2.exe in it.
If it reports a permissions problem, right-click the file and
choose Run as administrator.


التثبيت على لينكس / Installing on Linux
----------------------------------------------------------------
    ./install.sh

ولتحديد مسار اللعبة يدويًا / to give the path yourself:

    ./install.sh "/path/to/Risk of Rain 2"

وإن ظهرت Permission denied، فمدير الملفات لم يحفظ صلاحية التنفيذ:
    chmod +x install.sh && ./install.sh


تشغيل التعريب / Turning it on
----------------------------------------------------------------
شغّل اللعبة، اضغط قائمة اللغات في أعلى يمين الشاشة، واختر "العربية".
اختر اللغة من داخل اللعبة لا من ملف الإعدادات: اللعبة تحفظ
اللغة في Steam Cloud وتستعيدها فوق أي تعديل يدوي.

Start the game, open the language menu at the top right, and choose
العربية. Pick it in-game rather than by editing config.cfg: the game
stores the language in Steam Cloud and restores it over any hand edit.


الإزالة / Removing it
----------------------------------------------------------------
ويندوز: شغّل install-windows.bat واضغط "إزالة".
لينكس:  ./install.sh --uninstall

Windows: run install-windows.bat and click إزالة (Uninstall).
Linux:   ./install.sh --uninstall


النسخة المدعومة / Supported version
----------------------------------------------------------------
اللعبة 1.4.1#912. إن حُدِّثت اللعبة وبدا نص في غير موضعه، ثبّت أحدث
إصدار من التعريب فوق القديم.

Game 1.4.1#912. If the game updates and something looks off, install
the newest release of the translation over it.


ملاحظة / Note
----------------------------------------------------------------
التعريب لا يؤثر على اللعب الجماعي. فهو لا يرفع علامة "معدَّلة"
عن اللعبة، ولذلك تبقى في نفس قوائم المضيفين مع اللاعبين الآخرين،
وتبقى التحديات المنشوريّة تعمل.

The translation does not affect multiplayer. It never sets the
game's "modded" flag, so you stay in the same lobby pool as
everyone else and Prismatic Trials keep working.


ما لم يُعرَّب / What is left in English
----------------------------------------------------------------
أسماء صنّاع اللعبة في قائمة الشكر، ونصوص المحرّك والتراخيص،
وبعض مداخل السجلّ الخاصة بالأغراض. وهذه مقصودة.

The credits (they are people's names), the engine and legal
strings, and some item logbook entries. That is deliberate.


المزيد / More
----------------------------------------------------------------
https://github.com/UPdullah895/Risk-of-Rain-2-arabic
README.txt هو هذا الملف. LICENSE.txt رخصة الشيفرة (MIT).
licences/ رخص الخطوط المستخدمة.
