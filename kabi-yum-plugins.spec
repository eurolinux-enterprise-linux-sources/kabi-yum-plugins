Name:		kabi-yum-plugins
Version:	1.0
Release:	3%{?dist}
Summary:	The Red Hat Enterprise Linux kernel ABI yum plugin

Group:		System Environment/Kernel
License:	GPLv2
URL:		http://www.redhat.com/
Source0:	kabi-yum-plugins-%{version}.tar.bz2
Patch0:		kabi-yum-plugins-current.patch
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:	noarch

BuildRequires:	python
Requires:	kernel-abi-whitelists
Requires:	python
Requires:	yum >= 3.2.25-12

%description
The kABI yum plugins package contains a yum plugin that can be used in order
to enforce that only those third party kernel module packages meeting Red Hat
kernel ABI requirements are installed. The plugin requires that those drivers
be packaged in accordance with Red Hat Driver Update Program guidelines.

%prep
%setup -q
%patch0 -p1

%build
make

%install
rm -rf $RPM_BUILD_ROOT
make install PREFIX=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/usr/lib/yum-plugins/kabi.*
%config(noreplace) %{_sysconfdir}/yum/pluginconf.d/kabi.conf

%changelog
* Thu Sep 11 2014 Jiri Olsa <jolsa@redhat.com> - 1.0-3
- Fix kabi location path. (BZ#1112731)

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.0-2
- Mass rebuild 2013-12-27

* Thu Aug 08 2013 Jiri Olsa <jolsa@redhat.com> - 1.0-1
- fix kernel-abi-whitelists dependency
- Resolves: #994409

* Mon Jul 22 2013 Jiri Olsa <jolsa@redhat.com> - 1.0-0
- import from RHEL6.5
- Resolves: #980235
