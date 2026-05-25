import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import climate
from esphome.const import CONF_ID
from . import dometic_cfx_ble_ns, DometicCfxBle, CONF_DOMETIC_CFX_BLE_ID

DometicCfxBleClimate = dometic_cfx_ble_ns.class_(
    "DometicCfxBleClimate", climate.Climate, cg.Component
)

CONFIG_SCHEMA = climate.climate_schema(DometicCfxBleClimate).extend({
    cv.Required(CONF_DOMETIC_CFX_BLE_ID): cv.use_id(DometicCfxBle),
}).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await climate.register_climate(var, config)
    parent = await cg.get_variable(config[CONF_DOMETIC_CFX_BLE_ID])
    cg.add(var.set_parent(parent))
    cg.add(parent.add_entity("CLIMATE", var))
