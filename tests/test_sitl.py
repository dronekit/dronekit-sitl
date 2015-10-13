from dronekit_sitl import SITL
from nose.tools import assert_equals

copter_args = ['-I0', '-S', '--model', 'quad', '--home=-35.363261,149.165230,584,353']

def test_sitl():
    sitl = SITL('copter', '3.3-rc5')
    sitl.download()
    sitl.launch(copter_args)
    sitl.block_until_ready()
    assert_equals(sitl.poll(), None, 'SITL should still be running.')
    sitl.stop()
    assert sitl.poll() != None, 'SITL should stop running after kill.'

    # Test "relaunch"
    sitl.launch(copter_args)
    try:
    	sitl.launch(copter_args)
    	assert False, 'SITL should fail to launch() again when running'
    except:
    	pass
    try:
    	sitl.launch(copter_args, restart=True)
    except:
    	assert False, 'SITL should succeed in launch() when restart=True'

    sitl.stop()
