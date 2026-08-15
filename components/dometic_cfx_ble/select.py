import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import select
from esphome.const import CONF_TYPE
from . import (
    dometic_cfx_ble_ns,
    DometicCfxBle,
    CONF_DOMETIC_CFX_BLE_ID,
    validate_topic_type,
)

DEPENDENCIES = ["dometic_cfx_ble"]

DometicCfxBleSelect = dometic_cfx_ble_ns.class_(
    "DometicCfxBleSelect", select.Select, cg.PollingComponent
)

# Battery protection levels in device order (index 0/1/2).
BATTERY_PROTECTION_OPTIONS = ["Low", "Medium", "High"]

CONFIG_SCHEMA = (
    select.select_schema(DometicCfxBleSelect)
    .extend(
        {
            cv.Required(CONF_DOMETIC_CFX_BLE_ID): cv.use_id(DometicCfxBle),
            cv.Required(CONF_TYPE): validate_topic_type,
        }
    )
    .extend(cv.polling_component_schema("60s"))
)


async def to_code(config):
    var = await select.new_select(config, options=BATTERY_PROTECTION_OPTIONS)
    await cg.register_component(var, config)
    parent = await cg.get_variable(config[CONF_DOMETIC_CFX_BLE_ID])
    cg.add(var.set_parent(parent))
    cg.add(var.set_topic(config[CONF_TYPE]))
    cg.add(parent.add_entity(config[CONF_TYPE], var))
