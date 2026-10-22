pragma Singleton
import QtQuick 2.15

QtObject {
    id: theme

    // Estado reactivo del tema: "dark" o "light"
    property string activeTheme: "dark"

    // ── Superficies y Fondos ─────────────────────────────────────────────────
    readonly property color bgBase:     activeTheme === "dark" ? "#070E1C" : "#EEF2F7"
    readonly property color bgSurface:  activeTheme === "dark" ? "#10192A" : "#FFFFFF"
    readonly property color bgElevated: activeTheme === "dark" ? "#1A263A" : "#E2E8F0"
    readonly property color bgInput:    activeTheme === "dark" ? "#0C1422" : "#F8FAFC"
    readonly property color bgSidebar:  activeTheme === "dark" ? "#0A1222" : "#FFFFFF"
    readonly property color bgCard:     activeTheme === "dark" ? "#121E33" : "#FFFFFF"

    // ── Colores de Acento y Marca ────────────────────────────────────────────
    readonly property color accentPrimary:        "#1FA8FF"
    readonly property color accentPrimaryHover:   Qt.lighter(accentPrimary, 1.15)
    readonly property color accentPrimaryPressed: Qt.darker(accentPrimary, 1.20)
    readonly property color accentPurple:         "#8B5CF6"
    readonly property color accentSuccess:        "#10B981"
    readonly property color accentDanger:         "#EF4444"
    readonly property color accentWarning:        "#F59E0B"
    readonly property color accentInfo:           "#06B6D4"

    // ── Tipografía y Colores de Texto ────────────────────────────────────────
    readonly property color textPrimary:   activeTheme === "dark" ? "#F0F6FF" : "#0F172A"
    readonly property color textSecondary: activeTheme === "dark" ? "#8DA4BF" : "#64748B"
    readonly property color textMuted:     activeTheme === "dark" ? "#56697D" : "#94A3B8"
    readonly property color textOnAccent:  "#FFFFFF"

    readonly property string fontFamily: "Segoe UI, Inter, Arial, sans-serif"

    // ── Bordes y Separadores ─────────────────────────────────────────────────
    readonly property color borderSubtle: activeTheme === "dark" ? "#1E3048" : "#E2E8F0"
    readonly property color borderFocus:  accentPrimary

    // ── Radios de Esquinas ───────────────────────────────────────────────────
    readonly property int radiusXs: 4
    readonly property int radiusSm: 8
    readonly property int radiusMd: 12
    readonly property int radiusLg: 16
    readonly property int radiusXl: 24

    // ── Duraciones de Animación ──────────────────────────────────────────────
    readonly property int animFast: 140
    readonly property int animBase: 240
    readonly property int animSlow: 400

    // ── Tokens Liquid Glass (Glassmorphism Profesional) ──────────────────────
    readonly property color glassFill: activeTheme === "dark"
                                       ? Qt.rgba(0.06, 0.12, 0.22, 0.85)
                                       : Qt.rgba(1.00, 1.00, 1.00, 0.88)

    readonly property color glassBorder: activeTheme === "dark"
                                         ? Qt.rgba(1.0, 1.0, 1.0, 0.12)
                                         : Qt.rgba(0.0, 0.0, 0.0, 0.08)

    readonly property color glassHighlight: activeTheme === "dark"
                                            ? Qt.rgba(0.12, 0.66, 1.0, 0.12)
                                            : Qt.rgba(0.12, 0.66, 1.0, 0.08)
}
