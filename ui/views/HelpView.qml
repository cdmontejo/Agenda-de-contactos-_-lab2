import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true

    Column {
        width: parent.width
        spacing: 20
        padding: 24

        Column {
            spacing: 4
            Text {
                text: "Manual Técnico y Guía de Operaciones"
                font.pixelSize: 20
                font.weight: Font.Bold
                font.family: Theme.fontFamily
                color: Theme.textPrimary
            }
            Text {
                text: "Fundamentos teóricos y matemáticos de las operaciones de bajo nivel del Laboratorio No. 2"
                font.pixelSize: 13
                font.family: Theme.fontFamily
                color: Theme.textSecondary
            }
        }

        // ── 1. Estructura de Registros ─────────────────────────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 220

            Column {
                anchors.fill: parent
                spacing: 10

                Text {
                    text: "1. REGISTROS DE TAMAÑO FIJO (256 BYTES) Y UTF-8"
                    font.pixelSize: 12
                    font.weight: Font.Bold
                    color: Theme.accentPrimary
                }

                Text {
                    width: parent.width
                    text: "En sistemas operativos modernos, un carácter UTF-8 puede ocupar de 1 a 4 bytes. Para garantizar que cada contacto ocupe exactamente 256 bytes en 'contactos.dat', la función pack_field() mide la longitud en BYTES reales. Si el texto supera el tamaño del campo, elimina caracteres uno a uno verificando que no se rompan secuencias multibyte (evitando truncar a la mitad una tilde o una 'ñ'). Luego, rellena con espacios (0x20) hasta el tamaño estricto."
                    font.pixelSize: 12
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                    wrapMode: Text.Wrap
                }

                Text {
                    text: "Estructura del Registro: ID (10B) + Nombre (80B) + Teléfono (20B) + Correo (80B) + Ciudad (50B) + Estado (1B) + Padding (14B) + Newline (1B) = 256 Bytes exactos."
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                    color: Theme.accentPurple
                }
            }
        }

        // ── 2. Acceso Aleatorio O(1) con seek() y tell() ──────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 180

            Column {
                anchors.fill: parent
                spacing: 10

                Text {
                    text: "2. RIGOR MATEMÁTICO DEL ACCESO ALEATORIO CON seek() Y tell()"
                    font.pixelSize: 12
                    font.weight: Font.Bold
                    color: Theme.accentSuccess
                }

                Text {
                    width: parent.width
                    text: "• Búsqueda Directa O(1): Se consulta el ID en 'indice.json' en memoria para obtener el número de registro físico (record_num). Luego se posiciona el cabezal del archivo con f.seek(record_num * 256, os.SEEK_SET).\n• Demostración con tell(): Antes y después de cada lectura o escritura, f.tell() devuelve la posición exacta en bytes. El inspector de la aplicación muestra estos punteros en vivo.\n• Modificación In-Place: Al editar un contacto, se abre el archivo en 'r+b', se posiciona con seek() y se escriben 256 bytes. El tamaño total del archivo permanece invariable y ningún otro registro se ve alterado."
                    font.pixelSize: 12
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                    wrapMode: Text.Wrap
                }
            }
        }

        // ── 3. Integridad Criptográfica SHA-256 ────────────────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 160

            Column {
                anchors.fill: parent
                spacing: 10

                Text {
                    text: "3. INTEGRIDAD CRIPTOGRÁFICA SHA-256 Y DETECCIÓN DE ALTERACIONES"
                    font.pixelSize: 12
                    font.weight: Font.Bold
                    color: Theme.accentDanger
                }

                Text {
                    width: parent.width
                    text: "Cada vez que se añade, edita o elimina un contacto, el sistema calcula el digest SHA-256 en bloques de 8192 bytes de 'contactos.dat' y lo persiste atómicamente en 'contactos.sha256'. Si alguien modifica el archivo fuera de la aplicación (por ejemplo con un editor de texto o inyectando bytes), el hash diferirá del guardado y la alarma visual del Centro de Integridad alertará inmediatamente la rotura del sello."
                    font.pixelSize: 12
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                    wrapMode: Text.Wrap
                }
            }
        }
    }
}

