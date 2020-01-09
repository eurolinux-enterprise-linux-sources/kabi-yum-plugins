# Makefile - invoke the python interpretor for compilation of the kabi plugin.
# 
# Copyright (C) 2010 Jon Masters <jcm@redhat.com>
#
# This file is licensed under the GNU General Public License version 2.

PREFIX ?= /

INSTDIR ?= /usr/lib/yum-plugins
CONFDIR ?= /etc/yum/pluginconf.d
 
PROGNAME ?= kabi

%.pyc:	%.py
	python -c "import py_compile; py_compile.compile('$<')"

all:		${PROGNAME}.pyc

install:	all
		@mkdir -p ${PREFIX}/${INSTDIR}
		@mkdir -p ${PREFIX}/${CONFDIR}
		@install -m 644 ${PROGNAME}.py ${PREFIX}/${INSTDIR}
		@install -m 644 ${PROGNAME}.pyc ${PREFIX}/${INSTDIR}
		@install -m 644 *.conf ${PREFIX}/${CONFDIR}

clean:
		rm -rf *.pyc *.pyo *~ *.bak *.tar.gz
