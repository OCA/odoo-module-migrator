from lxml import etree


def replace_openerp_tag(xml_file):
    tree = etree.parse(xml_file)
    tree.Element("openerp").name = "odoo"
    tree.Element("data").remove()


_FUNCTIONS = {replace_openerp_tag}
