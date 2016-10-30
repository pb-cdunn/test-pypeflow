PYTHONPATH:=$(shell pwd):${PYTHONPATH}
export PYTHONPATH

default:
	@echo -n 'Try: make run'
distclean:
	git clean -xdf
clean:
	rm -rf mypwatcher/ all.log hey*/
run:
	./run.py foo.ini logging.json
mj:
	. ~mhsieh/Works/20161013_SAT348/pitchfork/deployment/setup-env.sh && ./run.py foo.ini logging.json
