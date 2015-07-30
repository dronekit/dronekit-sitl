from dronekit.sitl import SITL
from nose.tools import assert_equals

def test_sitl():
    sitl = SITL('copter', '3.3-rc5')
    sitl.download()
    sitl.launch(['-I0', '-S', '--model', 'quad', '--home=-35.363261,149.165230,584,353'])
    sitl.block_until_ready()
    assert_equals(sitl.poll(), None, 'SITL should still be running.')
    sitl.stop()
    assert sitl.poll() != None, 'SITL should stop running after kill.'
    assert sitl.poll() != 0, 'SITL should have died with error code.'
