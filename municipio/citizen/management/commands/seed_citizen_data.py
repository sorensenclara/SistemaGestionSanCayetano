from django.core.management.base import BaseCommand
from citizen.models import Area, CategoriaGestion, EstadoGestion


class Command(BaseCommand):
    help = "Carga datos iniciales de App Ciudadana"

    def handle(self, *args, **options):
        areas = [
            "Servicios Públicos",
            "Obras Públicas",
            "Dirección Vial",
            "Catastro",
        ]

        area_objs = {}
        for nombre in areas:
            area, _ = Area.objects.get_or_create(nombre=nombre)
            area_objs[nombre] = area

        estados = [
            ("pendiente", "Pendiente", "Tu gestión fue enviada correctamente y está pendiente de recepción por el Municipio."),
            ("en-analisis", "En Análisis", "Tu gestión está siendo analizada por el área correspondiente."),
            ("en-ejecucion", "En Ejecución", "Tu gestión fue asignada al área responsable y se encuentra en proceso de ejecución."),
            ("resuelto", "Resuelto", "Tu gestión fue resuelta correctamente."),
            ("rechazado", "Rechazado", "Tu gestión no pudo ser aprobada. Consultá el motivo informado por el Municipio."),
            ("observado", "Observado", "Tu gestión requiere una observación o ampliación de información."),
        ]

        for orden, (codigo, nombre, descripcion) in enumerate(estados, start=1):
            EstadoGestion.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "descripcion_ciudadano": descripcion,
                    "orden": orden,
                    "activo": True,
                },
            )

        reclamos = {
            "Servicios Públicos": [
                "Recolección de residuos no domiciliarios",
                "Pastos o malezas altas",
                "Sepulturas, nichos o panteones en mal estado",
                "Mantenimiento de espacios verdes",
                "Poda que afecta cables o viviendas",
                "Raíces que rompen veredas",
                "Mantenimiento de edificios y espacios públicos",
                "Poda sin autorización",
                "Juegos o mobiliario en mal estado",
                "Limpieza de calle",
                "Alumbrado de espacios públicos en mal estado",
            ],
            "Obras Públicas": [
                "Calles con baches o elevaciones",
                "Veredas en mal estado",
                "Desagües con falta de mantenimiento",
                "Entubamientos o alcantarillas a colocar",
                "Alumbrado público defectuoso",
                "Canalizaciones defectuosas",
                "Falta de compuertas o reguladores hídricos",
                "Puentes con falta de mantenimiento",
                "Fallas en obras realizadas",
                "Marcaciones viales",
            ],
            "Dirección Vial": [
                "Caminos en mal estado",
                "Mantenimiento de alcantarillas",
                "Agua estancada",
                "Acumulación de barro en caminos",
                "Mantenimiento de cunetas",
                "Mantenimiento de desagües",
                "Falta de nivelación",
            ],
            "Catastro": [
                "Corrección de datos físicos",
                "Errores de nomenclatura o ubicación de parcelas",
                "Corregir lugar de envío de correspondencia",
                "Regular titularidad de parcelas",
                "Parcelas mal categorizadas impositivamente",
                "Error en altura domiciliaria",
            ],
        }

        solicitudes = {
            "Servicios Públicos": [
                "Regador",
                "Desmalezadora",
                "Cortadora de césped autopropulsada",
                "Elevador",
                "Camión atmosférico",
                "Contenedores",
                "Camión y pala",
                "Provisión de agua",
                "Corte de pasto",
                "Extracción de plantas",
                "Limpieza de terrenos",
                "Poda de árbol",
                "Servicio de hidroelevador",
                "Limpieza de pozo sumidero",
                "Servicio de barredora",
                "Servicio de regador",
                "Colocación de planta",
                "Alquiler de escenario",
                "Recolección de residuos o restos de obra",
            ],
            "Obras Públicas": [
                "Minicargadora",
                "Minicargadora con martillo",
                "Minicargadora con retro",
                "Venta de hormigón",
                "Alquiler de casilla",
                "Tractoelevador",
                "Limpieza de alcantarillas",
                "Ampliación de redes de infraestructura",
                "Recambio de luminarias",
                "Hoyadora",
                "Lomos de burro",
                "Carga de materiales",
                "Apertura de calles",
                "Reparación de cordón cuneta",
                "Subida vehicular",
                "Nivelación de terrenos",
                "Pintar bajadas vehiculares",
            ],
            "Dirección Vial": [
                "Retropala",
                "Retro con orugas",
                "Topadora",
                "Rodillo autopropulsado",
                "Palas cargadoras",
                "Camiones",
                "Bateas",
                "Chasis",
                "Tractor",
                "Motoniveladoras",
                "Rodillo de arrastre",
                "Regador grande",
                "Provisión de tosca",
                "Provisión de tierra",
                "Colocación de tubos",
                "Repaso y alteo de caminos",
                "Aperturas de calle",
                "Entoscado de caminos",
                "Transporte de materiales",
            ],
            "Catastro": [
                "Certificado de altura domiciliaria",
                "Cambio de titularidad y correspondencia",
                "Informes catastrales",
                "Consultas sobre planos de obra o mensura",
                "Armado de planos específicos del partido",
                "Copia de cédula o planchetas",
            ],
        }

        tramites = {
            "Catastro": [
                "Cambio de titularidad",
                "Certificados",
                "Solicitud de inspección",
            ],
        }

        def palabras_clave(nombre):
            base = nombre.lower()
            extras = {
                "poda": "árbol, arbol, ramas, cable, vivienda, vereda",
                "alumbrado": "luz, luminaria, lámpara, lampara, poste",
                "baches": "calle, pozo, elevación, elevacion",
                "residuos": "basura, restos, recolección, recoleccion",
                "catastro": "parcela, plano, titularidad, domicilio, altura",
                "camiones": "camión, camion, transporte, materiales",
                "motoniveladoras": "camino, nivelación, nivelacion, vial",
            }

            claves = [base.replace(" ", ", ")]
            for palabra, extra in extras.items():
                if palabra in base:
                    claves.append(extra)

            return ", ".join(claves)

        def cargar_categoria(nombre, tipo, area_nombre, orden):
            CategoriaGestion.objects.update_or_create(
                nombre=nombre,
                tipo=tipo,
                area=area_objs[area_nombre],
                defaults={
                    "orden": orden,
                    "activa": True,
                    "palabras_clave": palabras_clave(nombre),
                },
            )

        for area_nombre, items in reclamos.items():
            for orden, nombre in enumerate(items, start=1):
                cargar_categoria(nombre, CategoriaGestion.TIPO_RECLAMO, area_nombre, orden)

        for area_nombre, items in solicitudes.items():
            for orden, nombre in enumerate(items, start=1):
                cargar_categoria(nombre, CategoriaGestion.TIPO_SOLICITUD, area_nombre, orden)

        for area_nombre, items in tramites.items():
            for orden, nombre in enumerate(items, start=1):
                cargar_categoria(nombre, CategoriaGestion.TIPO_TRAMITE, area_nombre, orden)

        self.stdout.write(self.style.SUCCESS("Datos iniciales cargados correctamente."))
