# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
from odoo_module_migrate.base_migration_script import BaseMigrationScript
from lxml import etree   
import os

""" Bucar todos los javascript y los css en los archivos xml y agregarlos al manifiesto del modulo de Odoo 
a la forma de Odoo 15 'assets': {
        'web.assets_backend': [
"""
def _get_files(module_path, reformat_file_ext):
    """Get files to be reformatted."""
    file_paths = list()
    if not module_path.is_dir():
        raise Exception(f"'{module_path}' is not a directory")
    file_paths.extend(module_path.rglob("*" + reformat_file_ext))
    return file_paths

def find_assets_in_xml(logger, module_path, module_name, manifest_path, migration_steps, tools):
    js_assets = set()
    css_assets = set()

    reformat_file_ext = ".xml"
    file_paths = _get_files(module_path, reformat_file_ext)
    logger.debug(f"{reformat_file_ext} files found:\n" f"{list(map(str, file_paths))}")
    print(f"{reformat_file_ext} files found:\n" f"{list(map(str, file_paths))}")

    # Recorre todos los archivos XML en el directorio del módulo
    for file_path in file_paths:
        xml_file_path = str(file_path)
        xml_tree = etree.parse(xml_file_path)

        # Encuentra los elementos que contienen rutas a archivos JavaScript y CSS
        for element in xml_tree.xpath("//script"):
            js_src = element.get("src")
            if js_src:
                js_assets.add(js_src)
                print(js_src)
            # Comenta el elemento para que no interrumpa
            comment_element(xml_tree, element)

        for element in xml_tree.xpath("//link[@rel='stylesheet']"):
            css_href = element.get("href")
            if css_href:
                css_assets.add(css_href)
                print(css_href)
            # Comenta el elemento para que no interrumpa
            comment_element(xml_tree, element)

        # Guarda los cambios en el archivo XML
        with open(xml_file_path, 'w') as xml_file:
            xml_file.write(etree.tostring(xml_tree, encoding="unicode"))

    update_manifest(manifest_path, js_assets, css_assets)

def comment_element(xml_tree, element):
    comment = etree.Comment(element.text)
    parent = element.getparent()
    parent.replace(element, comment)


def update_manifest(manifest_path, js_assets, css_assets):
    # Abre el archivo del manifiesto para lectura y escritura
    with open(manifest_path, 'r') as file:
        manifest_data = file.read()

        # Encuentra la ubicación donde se debe insertar las rutas de los activos
        insert_index = manifest_data.find("'web.assets_backend': [")
    
        # Construye las secciones de activos
        js_assets_section = "\n".join([f"            '{js_asset}'," for js_asset in js_assets])
        css_assets_section = "\n".join([f"            '{css_asset}'," for css_asset in css_assets])

        # Actualiza el manifiesto con las rutas de los activos
        updated_manifest_data = manifest_data[:insert_index] + f"""'assets': {{
        'web.assets_backend': [
            {js_assets_section + 
             css_assets_section}
                    ],
                }},
            """
        if insert_index == -1:
            #añañde las rutas de los activos al final del manifiesto 
            updated_manifest_data = manifest_data + f"""'assets': {{
        'web.assets_backend': [
             {js_assets_section + 
              css_assets_section}
                    ],
                }},
            """
        # Escribe el manifiesto actualizado

        with open(manifest_path, 'w') as file:
            file.write(updated_manifest_data)


#Remplazar  self.env['bus.bus'].sendone por self.env['bus.bus']._sendone
_TEXT_REPLACES = {
    ".py": {
        r"self\.env\['bus\.bus'\]\.sendone": "self.env['bus.bus']._sendone",
    },
}

class MigrationScript(BaseMigrationScript):
    """Migration script for Odoo 14.0."""

    _GLOBAL_FUNCTIONS = [find_assets_in_xml]
    _TEXT_REPLACES = _TEXT_REPLACES

