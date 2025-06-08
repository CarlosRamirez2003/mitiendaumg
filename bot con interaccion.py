import pymysql
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
    filters
)
import logging
from dotenv import load_dotenv
import os
import json
import time

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración de MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': 'TIENDA_TECNOLOGICA',
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '32791'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'cursorclass': pymysql.cursors.DictCursor
}

TOKEN = os.getenv('TOKEN', "7962183508:AAH6WdIW92wvbF69xS6WxlzQUjHnqUq83No")

def get_db_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        logger.info("✅ Conexión a MySQL exitosa")
        return conn
    except Exception as e:
        logger.error(f"❌ Error en MySQL: {e}")
        raise

# Función para mostrar productos por categoría
async def mostrar_productos(update: Update, categoria: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre, precio_actual 
                FROM productos 
                WHERE LOWER(categoria) = LOWER(%s) 
                LIMIT 5
            """, (categoria,))
            productos = cursor.fetchall()
            
            if productos:
                keyboard = [
                    [InlineKeyboardButton(f"{p['nombre']} - ${p['precio_actual']:.2f}", 
                      callback_data=f"detalle:{p['id']}")]
                    for p in productos
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"📱 {categoria.capitalize()} disponibles:",
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(f"No encontré productos en la categoría {categoria}")
    except Exception as e:
        logger.error(f"Error al mostrar productos: {e}")
        await update.message.reply_text("⚠️ Ocurrió un error al buscar productos")
    finally:
        conn.close()

# Comando /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📱 Celulares", callback_data='celulares')],
        [InlineKeyboardButton("💻 Laptops", callback_data='laptops')],
        [InlineKeyboardButton("🖨️ Impresoras", callback_data='impresoras')],
        [InlineKeyboardButton("🎧 Accesorios", callback_data='accesorios')],
        [InlineKeyboardButton("⌚ Smartwatches", callback_data='smartwatches')],
        [InlineKeyboardButton("🎧 Auriculares", callback_data='auriculares')],
        [InlineKeyboardButton("🎮 Consolas", callback_data='consolas')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 ¡Hola {user.first_name}! Soy tu asistente de compras.\n"
        "Elige una categoría o dime qué producto buscas.",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    # Mostrar detalle del producto
    if data.startswith('detalle:'):
        producto_id = int(data.split(':')[1])
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre, descripcion, precio_actual, categoria, stock, especificaciones
                FROM productos
                WHERE id = %s
            """, (producto_id,))
            producto = cursor.fetchone()
        conn.close()

        if not producto:
            await query.edit_message_text("Producto no encontrado.")
            return

        espec_text = ''
        if producto['especificaciones']:
            try:
                espec_json = json.loads(producto['especificaciones'])
                espec_text = '\n'.join([f"- {k}: {v}" for k,v in espec_json.items()])
            except Exception:
                espec_text = 'No se pudo mostrar especificaciones.'

        mensaje = (
            f"🛍️ Detalle de producto:\n\n"
            f"Nombre: {producto['nombre']}\n"
            f"Categoría: {producto['categoria']}\n"
            f"Precio: ${producto['precio_actual']:.2f}\n"
            f"Stock: {producto['stock']}\n"
            f"Descripción: {producto['descripcion'] or 'Sin descripción'}\n"
            f"Especificaciones:\n{espec_text}\n\n"
            "¿Quieres agregarlo al carrito?"
        )
        keyboard = [
            [InlineKeyboardButton("🛒 Agregar al carrito", callback_data=f"agregar:{producto['id']}")],
            [InlineKeyboardButton("⬅️ Volver a productos", callback_data=f"{producto['categoria'].lower()}:1")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(mensaje, reply_markup=reply_markup)
        return

    # Agregar producto al carrito
    if data.startswith('agregar:'):
        producto_id = int(data.split(':')[1])
        if 'carrito' not in context.user_data:
            context.user_data['carrito'] = []
        context.user_data['carrito'].append(producto_id)
        await query.edit_message_text("✅ Producto agregado al carrito.\n\n"
                                    "Puedes seguir navegando o enviar /carrito para ver tu carrito.")
        return

    # Vaciar carrito
    if data == "vaciar_carrito":
        context.user_data['carrito'] = []
        await query.edit_message_text("🗑️ Carrito vaciado correctamente.")
        return
        
    # Procesar pago
    elif data == "pagar_tarjeta":
        carrito = context.user_data.get('carrito', [])
        if not carrito:
            await query.edit_message_text("❌ El carrito está vacío.")
            return
            
        await query.edit_message_text("💳 Procesando pago con tarjeta...")
        time.sleep(2)
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            format_strings = ','.join(['%s'] * len(carrito))
            cursor.execute(f"SELECT SUM(precio_actual) as total FROM productos WHERE id IN ({format_strings})", carrito)
            total = cursor.fetchone()['total']
        conn.close()
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"✅ Pago exitoso por ${total:.2f}\n\n"
                 "📦 Tu pedido está siendo procesado.\n"
                 "¡Gracias por tu compra!"
        )
        context.user_data['carrito'] = []
        return
        
    # Generar factura
    elif data == "generar_factura":
        carrito = context.user_data.get('carrito', [])
        if not carrito:
            await query.edit_message_text("❌ El carrito está vacío.")
            return
            
        conn = get_db_connection()
        with conn.cursor() as cursor:
            format_strings = ','.join(['%s'] * len(carrito))
            cursor.execute(f"SELECT nombre, precio_actual FROM productos WHERE id IN ({format_strings})", carrito)
            productos = cursor.fetchall()
            cursor.execute(f"SELECT SUM(precio_actual) as total FROM productos WHERE id IN ({format_strings})", carrito)
            total = cursor.fetchone()['total']
        conn.close()
        
        factura = "📄 **Factura de compra**\n\n"
        factura += "📋 Productos:\n"
        for p in productos:
            factura += f"- {p['nombre']}: ${p['precio_actual']:.2f}\n"
        factura += f"\n💵 Total: ${total:.2f}\n\n"
        factura += "⚠️ Esta es una factura simulada"
        
        await query.edit_message_text(factura, parse_mode='Markdown')
        return

    # Categoría con paginación
    if ':' in data:
        category, page = data.split(':')
        page = int(page)
    else:
        category = data
        page = 1

    page_size = 10
    offset = (page - 1) * page_size

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM productos WHERE LOWER(categoria) = %s", (category.lower(),))
        total = cursor.fetchone()['total']
        cursor.execute("""
            SELECT id, nombre, precio_actual 
            FROM productos 
            WHERE LOWER(categoria) = %s 
            LIMIT %s OFFSET %s
        """, (category.lower(), page_size, offset))
        productos = cursor.fetchall()
    conn.close()

    if not productos:
        await query.edit_message_text(f"No hay productos en la categoría {category}.")
        return

    botones_productos = [
        [InlineKeyboardButton(f"{prod['nombre']} - ${prod['precio_actual']:.2f}", callback_data=f"detalle:{prod['id']}")]
        for prod in productos
    ]

    paginacion_botones = []
    if offset > 0:
        paginacion_botones.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f"{category}:{page-1}"))
    if offset + page_size < total:
        paginacion_botones.append(InlineKeyboardButton("➡️ Siguiente", callback_data=f"{category}:{page+1}"))

    if paginacion_botones:
        botones_productos.append(paginacion_botones)

    reply_markup = InlineKeyboardMarkup(botones_productos)
    await query.edit_message_text(
        f"📋 Productos en {category.capitalize()} (página {page}):\n\n"
        "Elige un producto para ver detalles:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text.lower()
    
    # Mapeo de categorías
    categorias = {
        'celular': 'celulares',
        'laptop': 'laptops',
        'impresora': 'impresoras',
        'accesorio': 'accesorios',
        'smartwatch': 'smartwatches',
        'auricular': 'auriculares',
        'consola': 'consolas',
        'tablet': 'tablets'
    }
    
    # Buscar categoría en el mensaje
    categoria_detectada = None
    for keyword, categoria in categorias.items():
        if keyword in text:
            categoria_detectada = categoria
            break
    
    if categoria_detectada:
        await mostrar_productos(update, categoria_detectada)
    elif any(palabra in text for palabra in ['presupuesto', 'tengo', 'dólares', '$']):
        try:
            presupuesto = float(''.join(filter(str.isdigit, text)))
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, nombre, precio_actual, categoria 
                    FROM productos 
                    WHERE precio_actual <= %s 
                    ORDER BY precio_actual DESC 
                    LIMIT 5
                """, (presupuesto,))
                productos = cursor.fetchall()
            conn.close()

            if not productos:
                await update.message.reply_text(f"No encontré productos bajo ${presupuesto:.2f}.")
                return

            keyboard = [
                [InlineKeyboardButton(
                    f"{p['nombre']} (${p['precio_actual']:.2f}) - {p['categoria']}",
                    callback_data=f"detalle:{p['id']}"
                )] for p in productos
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"💡 Recomendaciones (hasta ${presupuesto:.2f}):",
                reply_markup=reply_markup
            )
        except ValueError:
            await update.message.reply_text("Por favor, escribe tu presupuesto con un número válido (ej: 500 dólares).")
    else:
        await update.message.reply_text(
            "No entendí. Puedes:\n"
            "- Preguntar por una categoría (ej: celulares, laptops)\n"
            "- Decirme tu presupuesto (ej: 'tengo 500 dólares')\n"
            "- Usar /menu para ver categorías"
        )

async def carrito(update: Update, context: CallbackContext) -> None:
    carrito = context.user_data.get('carrito', [])
    if not carrito:
        await update.message.reply_text("Tu carrito está vacío.")
        return

    conn = get_db_connection()
    with conn.cursor() as cursor:
        format_strings = ','.join(['%s'] * len(carrito))
        cursor.execute(f"SELECT nombre, precio_actual FROM productos WHERE id IN ({format_strings})", carrito)
        productos = cursor.fetchall()
        cursor.execute(f"SELECT SUM(precio_actual) as total FROM productos WHERE id IN ({format_strings})", carrito)
        total = cursor.fetchone()['total']
    conn.close()

    mensaje = "🛒 Productos en tu carrito:\n\n"
    for p in productos:
        mensaje += f"- {p['nombre']} - ${p['precio_actual']:.2f}\n"
    mensaje += f"\n💵 Total: ${total:.2f}\n\n"
    mensaje += "¿Qué deseas hacer?"

    keyboard = [
        [InlineKeyboardButton("🗑️ Vaciar carrito", callback_data="vaciar_carrito")],
        [InlineKeyboardButton("💳 Pagar con tarjeta", callback_data="pagar_tarjeta")],
        [InlineKeyboardButton("📝 Generar factura", callback_data="generar_factura")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(mensaje, reply_markup=reply_markup)

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("carrito", carrito))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    try:
        logger.info("🤖 Bot iniciado... Presiona Ctrl+C para detener")
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido manualmente")
    except Exception as e:
        logger.error(f"🔥 Error crítico: {e}")
    finally:
        if application.running:
            application.stop()
            application.shutdown()

if __name__ == '__main__':
    main()