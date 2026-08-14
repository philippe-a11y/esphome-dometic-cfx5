import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import select
from esphome.const import CONF_ID, CONF_TYPE
from . import dometic_cfx_ble_ns, CONF_DOMETIC_CFX_BLE_ID, entity_schema

DEPENDENCIES = ["dometic_cfx_ble"]

DometicCfxBleSelect = dometic_cfx_ble_ns.class_("DometicCfxBleSelect", select.Select, cg.PollingComponent)

CONFIG_SCHEMA = entity_schema("select").extend(select.select_schema(DometicCfxBleSelect)).extend({
    cv.GenerateID(): cv.declare_id(DometicCfxBleSelect)
})

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    
    # Pre-populate the dropdown menu options
    await select.register_select(var, config, options=["Low", "Medium", "High"])

    parent = await cg.get_variable(config[CONF_DOMETIC_CFX_BLE_ID])
    cg.add(var.set_parent(parent))
    cg.add(var.set_topic(config[CONF_TYPE]))
    cg.add(parent.add_entity(config[CONF_TYPE], var))
