import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import climate
from esphome.const import CONF_ID
from . import dometic_cfx_ble_ns, DometicCfxBle, CONF_DOMETIC_CFX_BLE_ID

DometicCfxBleClimate = dometic_cfx_ble_ns.class_(
    "DometicCfxBleClimate", climate.Climate, cg.Component
)

CONF_COMPARTMENT = "compartment"

CONFIG_SCHEMA = climate.climate_schema(DometicCfxBleClimate).extend({
    cv.Required(CONF_DOMETIC_CFX_BLE_ID): cv.use_id(DometicCfxBle),
    # Which compartment this climate controls. 0 = single-zone (default),
    # 1 = second zone on dual-zone boxes (experimental, see README).
    cv.Optional(CONF_COMPARTMENT, default=0): cv.int_range(min=0, max=1),
}).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await climate.register_climate(var, config)
    parent = await cg.get_variable(config[CONF_DOMETIC_CFX_BLE_ID])
    cg.add(var.set_parent(parent))
    cg.add(var.set_compartment_index(config[CONF_COMPARTMENT]))
    key = "CLIMATE" if config[CONF_COMPARTMENT] == 0 else f"CLIMATE_{config[CONF_COMPARTMENT]}"
    cg.add(parent.add_entity(key, var))
