from sqlalchemy.orm import Session

import os
import csv

from models import (
    AreaOperacion,
    AreaOperacionDistrito,
    CatPais,
    CatDepartamento,
    CatProvincia,
    CatDistrito
)


class TerritorioService:

    @staticmethod
    def listar_areas(db: Session):

        return (
            db.query(AreaOperacion)
            .order_by(AreaOperacion.nombre)
            .all()
        )

    @staticmethod
    def obtener_area(
        db: Session,
        area_id: int
    ):

        return (
            db.query(AreaOperacion)
            .filter(
                AreaOperacion.id == area_id
            )
            .first()
        )

    @staticmethod
    def crear_area(
        db: Session,
        codigo: str,
        nombre: str,
        descripcion: str,
        radio_operacion: int,
        latitud: float,
        longitud: float
    ):

        area = AreaOperacion(

            codigo=codigo,

            nombre=nombre,

            descripcion=descripcion,

            radio_operacion=radio_operacion,

            latitud_centro=latitud,

            longitud_centro=longitud
        )

        db.add(area)

        db.commit()

        db.refresh(area)

        return area

    @staticmethod
    def listar_distritos_area(
        db: Session,
        area_id: int
    ):

        return (
            db.query(AreaOperacionDistrito)
            .filter(
                AreaOperacionDistrito.area_operacion_id == area_id
            )
            .all()
        )

    @staticmethod
    def asignar_distrito(
        db: Session,
        area_id: int,
        distrito_id: int
    ):

        existe = (
            db.query(AreaOperacionDistrito)
            .filter(
                AreaOperacionDistrito.area_operacion_id == area_id,
                AreaOperacionDistrito.distrito_id == distrito_id
            )
            .first()
        )

        if existe:
            return existe

        relacion = AreaOperacionDistrito(

            area_operacion_id=area_id,

            distrito_id=distrito_id
        )

        db.add(relacion)

        db.commit()

        db.refresh(relacion)

        return relacion

    @staticmethod
    def importar_ubigeo(db: Session):
    
        try:
    
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
            csv_file = os.path.join(
                base_dir,
                "data",
                "ubigeo",
                "UBIGEO 2022_1891 distritos.csv"
            )
    
            pais = db.query(CatPais).filter(
                CatPais.codigo_iso2 == "PE"
            ).first()
    
            if not pais:
                pais = CatPais(
                    nombre="Perú",
                    codigo_iso2="PE",
                    codigo_iso3="PER"
                )
                db.add(pais)
                db.flush()
    
            departamentos = {}
            provincias = {}
    
            dep_nuevos = 0
            prov_nuevas = 0
            dist_nuevos = 0
    
            with open(csv_file, encoding="utf-8-sig") as f:
    
                reader = csv.DictReader(f, delimiter=";")
    
                for fila in reader:
    
                    dep_nombre = fila["NOMBDEP"].strip().title()
                    prov_nombre = fila["NOMBPROV"].strip().title()
                    dist_nombre = fila["NOMBDIST"].strip().title()
                    ubigeo = fila["IDDIST"].strip()
    
                    dep = departamentos.get(dep_nombre)
    
                    if dep is None:
    
                        dep = db.query(CatDepartamento).filter(
                            CatDepartamento.pais_id == pais.id,
                            CatDepartamento.nombre == dep_nombre
                        ).first()
    
                        if not dep:
                            dep = CatDepartamento(
                                pais_id=pais.id,
                                nombre=dep_nombre,
                                ubigeo=ubigeo[:2]
                            )
                            db.add(dep)
                            db.flush()
                            dep_nuevos += 1
    
                        departamentos[dep_nombre] = dep
    
                    clave = (dep.id, prov_nombre)
    
                    prov = provincias.get(clave)
    
                    if prov is None:
    
                        prov = db.query(CatProvincia).filter(
                            CatProvincia.departamento_id == dep.id,
                            CatProvincia.nombre == prov_nombre
                        ).first()
    
                        if not prov:
                            prov = CatProvincia(
                                departamento_id=dep.id,
                                nombre=prov_nombre,
                                ubigeo=ubigeo[:4]
                            )
                            db.add(prov)
                            db.flush()
                            prov_nuevas += 1
    
                        provincias[clave] = prov
    
                    existe = db.query(CatDistrito).filter(
                        CatDistrito.ubigeo == ubigeo
                    ).first()
    
                    if existe:
                        continue
    
                    db.add(
                        CatDistrito(
                            provincia_id=prov.id,
                            nombre=dist_nombre,
                            ubigeo=ubigeo
                        )
                    )
    
                    dist_nuevos += 1
    
            db.commit()
    
            return {
                "ok": True,
                "departamentos": dep_nuevos,
                "provincias": prov_nuevas,
                "distritos": dist_nuevos
            }
    
        except Exception as e:
    
            db.rollback()
    
            return {
                "ok": False,
                "tipo": type(e).__name__,
                "error": str(e)
            }
