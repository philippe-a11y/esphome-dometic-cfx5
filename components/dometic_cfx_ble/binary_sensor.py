import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_TYPE
from esphome.components import binary_sensor as esphome_binary_sensor
from . import dometic_cfx_ble_ns, DometicCfxBle, CONF_DOMETIC_CFX_BLE_ID, validate_topic_type

DometicCfxBleBinarySensor = dometic_cfx_ble_ns.class_(
    "DometicCfxBleBinarySensor", esphome_binary_sensor.BinarySensor, cg.Component
)

CONFIG_SCHEMA = esphome_binary_sensor.binary_sensor_schema(DometicCfxBleBinarySensor).extend({
    cv.Required(CONF_DOMETIC_CFX_BLE_ID): cv.use_id(DometicCfxBle),
    cv.Required(CONF_TYPE): validate_topic_type,
}).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await esphome_binary_sensor.register_binary_sensor(var, config)
    parent = await cg.get_variable(config[CONF_DOMETIC_CFX_BLE_ID])
    cg.add(parent.add_entity(config[CONF_TYPE], var))
