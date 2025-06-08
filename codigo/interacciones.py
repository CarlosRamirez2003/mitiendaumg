import pymysql
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
import logging

# Configuración
load_dotenv()
logger = logging.getLogger(__name__)

class InteraccionesHandler:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': 'TIENDA_TECNOLOGICA',
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', '32791'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'cursorclass': pymysql.cursors.DictCursor
        }
        
        self.categorias = {
            'tablet': 'Tablets',
            'android': 'Tablets',
            'laptop': 'Laptops',
            'celular': 'Celulares',
            'smartwatch': 'Smartwatches',
            'auricular': 'Auriculares',
            'tv': 'Televisores',
            'consola': 'Consolas',
            'impresora': 'Impresoras',
            'regalo': 'Consolas'
        }

    def get_db_connection(self):
        try:
            return pymysql.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Error de conexión MySQL: {e}")
            raise

    async def mostrar_productos(self, update, categoria, mensaje_usuario):
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cursor:
                query = """
                    SELECT id, nombre, precio_actual 
                    FROM productos 
                    WHERE LOWER(categoria) = LOWER(%s) 
                    LIMIT 5
                """
                cursor.execute(query, (categoria,))
                productos = cursor.fetchall()

                if productos:
                    keyboard = [
                        [InlineKeyboardButton(
                            f"{p['nombre']} - ${p['precio_actual']:.2f}", 
                            callback_data=f"detalle:{p['id']}")]
                        for p in productos
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    respuesta = f"📱 {categoria.capitalize()} recomendados:\n(Elige para ver detalles)"
                    
                    if update.callback_query:
                        await update.callback_query.edit_message_text(respuesta, reply_markup=reply_markup)
                    else:
                        await update.message.reply_text(respuesta, reply_markup=reply_markup)
                    
                    await self.registrar_interaccion(
                        str(update.effective_user.id),
                        mensaje_usuario,
                        f"Mostré productos de {categoria}"
                    )
                else:
                    respuesta = f"No encontré productos en {categoria}"
                    if update.callback_query:
                        await update.callback_query.edit_message_text(respuesta)
                    else:
                        await update.message.reply_text(respuesta)
        except Exception as e:
            logger.error(f"Error al mostrar productos: {e}")
            await update.message.reply_text("⚠️ Error al buscar productos")
        finally:
            conn.close()

    async def registrar_interaccion(self, usuario_id, mensaje, respuesta):
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO interacciones_chatbot 
                    (usuario_id, mensaje, respuesta) 
                    VALUES (%s, %s, %s)
                """, (usuario_id, mensaje, respuesta))
                conn.commit()
        except Exception as e:
            logger.error(f"Error al registrar interacción: {e}")
        finally:
            conn.close()

    async def manejar_mensaje(self, update, context):
        user_message = update.message.text.lower()
        
        # Detección de categoría
        categoria = next(
            (cat for key, cat in self.categorias.items() if key in user_message),
            None
        )
        
        if categoria:
            await self.mostrar_productos(update, categoria, user_message)
        else:
            await update.message.reply_text(
                "No entendí qué producto buscas. Intenta con:\n"
                "- 'Tablets Android'\n- 'Consolas para regalo'\n"
                "- O usa /menu para ver categorías"
            )
