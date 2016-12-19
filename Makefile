PKGNAME = iniherit

test:
	nosetests --verbose

clean:
	find . -iname '*.pyc' -exec rm {} \;
	rm -fr "$(PKGNAME).egg-info" dist

tag:
	@echo "[  ] tagging as version `cat VERSION.txt`..."
	git tag -a "v`cat VERSION.txt`" -m "released v`cat VERSION.txt`"

ci:
	git push
	git push --tags

upload:
	python setup.py sdist upload
