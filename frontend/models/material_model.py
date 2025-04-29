class Material:
    def __init__(self, id_material, nombre, descripcion, unidad_medida, stock_minimo, stock_maximo):
        self.id_material = id_material
        self.nombre = nombre
        self.descripcion = descripcion
        self.unidad_medida = unidad_medida
        self.stock_minimo = stock_minimo
        self.stock_maximo = stock_maximo

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_material=data.get("id_material"),
            nombre=data.get("nombre", ""),
            descripcion=data.get("descripcion", ""),
            unidad_medida=data.get("unidad_medida", ""),
            stock_minimo=data.get("stock_minimo", 0),
            stock_maximo=data.get("stock_maximo", 0)
        )
