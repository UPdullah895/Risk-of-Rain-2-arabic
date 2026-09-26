using System;
using System.Collections.Generic;
using System.IO;
using Path = System.IO.Path;
using BepInEx;
using BepInEx.Logging;
using HarmonyLib;
using RoR2;
using TMPro;
using UnityEngine;
using UnityEngine.TextCore.LowLevel;

namespace RoR2Arabic
{
    /// <summary>
    /// Adds Arabic to Risk of Rain 2: registers an "ar" language folder and supplies a
    /// font that can actually draw Arabic glyphs.
    ///
    /// Deliberately does NOT reference R2API and never sets RoR2Application.isModded.
    /// That flag is what adds the "mod" lobby tag in PreGameController.UpdateTags, which
    /// splits matchmaking from vanilla players and disables Prismatic Trials. This plugin
    /// only adds text and glyphs - it touches no game state - so leaving the flag alone is
    /// both correct and what keeps multiplayer working normally.
    /// </summary>
    [BepInPlugin(Guid, "Risk of Rain 2 Arabic", "0.2.0")]
    public class ArabicPlugin : BaseUnityPlugin
    {
        public const string Guid = "com.updullah.ror2arabic";

        /// Name of the placeholder Font object. FontEnginePatch keys off this.
        internal const string FontName = "RoR2 Arabic";

        internal static ManualLogSource Log;
        internal static string TtfPath;

        private static string _pluginDir;
        private static TMP_FontAsset _arabic;
        private static readonly HashSet<int> Patched = new HashSet<int>();

        private void Awake()
        {
            Log = Logger;
            _pluginDir = Path.GetDirectoryName(Info.Location);
            TtfPath = Path.Combine(_pluginDir, "fonts", "RoR2Arabic-Regular.ttf");

            new Harmony(Guid).PatchAll(typeof(FontEnginePatch));

            Language.collectLanguageRootFolders += folders =>
            {
                string dir = Path.Combine(_pluginDir, "Language");
                if (Directory.Exists(dir)) folders.Add(dir);
                else Log.LogWarning($"language folder missing: {dir}");
            };
            Language.onCurrentLanguageChanged += OnCurrentLanguageChanged;

            Log.LogInfo($"loaded; isModded={RoR2Application.isModded} (stays false: multiplayer unaffected)");
        }

        private void Update()
        {
            // New scenes bring new TMP_FontAssets; keep the fallback attached to them.
            if (_arabic != null) ApplyFallback();
        }

        private static void OnCurrentLanguageChanged()
        {
            if (Language.currentLanguageName != "ar") return;
            Log.LogInfo("language -> ar");
            if (_arabic == null) _arabic = BuildFontAsset();
            if (_arabic != null) ApplyFallback(force: true);
        }

        private static TMP_FontAsset BuildFontAsset()
        {
            if (!File.Exists(TtfPath)) { Log.LogError($"font missing: {TtfPath}"); return null; }
            try
            {
                FontEngine.InitializeFontEngine();
                // The Font object is a name-only placeholder: FontEnginePatch intercepts every
                // FontEngine.LoadFontFace(Font, ...) for this name and loads the .ttf by path
                // instead. Unity cannot build a usable Font from a loose file at runtime, and
                // TMP's dynamic rasteriser only ever asks the engine for "the current face".
                var placeholder = new Font(FontName);
                var fa = TMP_FontAsset.CreateFontAsset(
                    placeholder, 90, 9, GlyphRenderMode.SDFAA, 1024, 1024,
                    AtlasPopulationMode.Dynamic, enableMultiAtlasSupport: true);
                if (fa == null) { Log.LogError("CreateFontAsset returned null"); return null; }
                fa.name = "RoR2Arabic SDF";
                Log.LogInfo($"built font asset: {fa.faceInfo.familyName} pt={fa.faceInfo.pointSize}");
                return fa;
            }
            catch (Exception ex) { Log.LogError($"font build failed: {ex}"); return null; }
        }

        /// <summary>Attach the Arabic font as a fallback on every other loaded TMP font.</summary>
        private static void ApplyFallback(bool force = false)
        {
            var all = Resources.FindObjectsOfTypeAll<TMP_FontAsset>();
            int added = 0;
            foreach (var a in all)
            {
                if (a == null || a == _arabic) continue;
                int id = a.GetInstanceID();
                if (!force && Patched.Contains(id)) continue;
                Patched.Add(id);
                if (a.fallbackFontAssetTable == null) a.fallbackFontAssetTable = new List<TMP_FontAsset>();
                if (!a.fallbackFontAssetTable.Contains(_arabic)) { a.fallbackFontAssetTable.Add(_arabic); added++; }
            }
            if (added > 0) Log.LogInfo($"Arabic fallback attached to {added} font asset(s)");
        }
    }

    /// <summary>
    /// TMP rasterises dynamic glyphs by calling FontEngine.LoadFontFace(Font, ...), which
    /// fails with Invalid_File for any Font that did not come from a Unity asset - verified
    /// on this build. Loading the same face by file path does work, so for our placeholder
    /// font we substitute the path overload.
    /// </summary>
    [HarmonyPatch(typeof(FontEngine))]
    internal static class FontEnginePatch
    {
        private static bool Redirect(Font font, int pointSize, ref FontEngineError result)
        {
            if (font == null || font.name != ArabicPlugin.FontName) return true;   // run original
            result = pointSize > 0
                ? FontEngine.LoadFontFace(ArabicPlugin.TtfPath, pointSize)
                : FontEngine.LoadFontFace(ArabicPlugin.TtfPath);
            return false;                                                          // skip original
        }

        [HarmonyPrefix, HarmonyPatch(nameof(FontEngine.LoadFontFace), typeof(Font))]
        private static bool LoadByFont(Font font, ref FontEngineError __result)
            => Redirect(font, 0, ref __result);

        [HarmonyPrefix, HarmonyPatch(nameof(FontEngine.LoadFontFace), typeof(Font), typeof(int))]
        private static bool LoadByFontSized(Font font, int pointSize, ref FontEngineError __result)
            => Redirect(font, pointSize, ref __result);

        [HarmonyPrefix, HarmonyPatch(nameof(FontEngine.LoadFontFace), typeof(Font), typeof(int), typeof(int))]
        private static bool LoadByFontSizedIndexed(Font font, int pointSize, ref FontEngineError __result)
            => Redirect(font, pointSize, ref __result);
    }
}
