from dronekit_sitl import SITL
from nose.tools import assert_equals,assert_is_not_none

copter_args = ['-I0', '-S', '--model', 'quad', '--home=-35.363261,149.165230,584,353']

def test_sitl():
    sitl = SITL()
    sitl.download('copter', '3.3')
    sitl.launch(copter_args)
    sitl.block_until_ready()

    assert_equals(sitl.poll(), None, 'SITL should still be running.')
    assert_equals(sitl.using_sim, False, 'SITL for copter-3.3 should not be using pysim')

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

def test_version_list():
    from dronekit_sitl import version_list
    versions = version_list()
    assert_is_not_none(versions)
    expected = [u'solo', u'plane', u'copter', u'rover']
    expected.sort()
    models = list(versions.keys())
    models.sort()
    assert_equals(expected, models)

def test_download():
    from dronekit_sitl import download
    download('copter','3.3', None)