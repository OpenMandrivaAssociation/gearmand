%define major 4
%define libname %mklibname gearman %{major}
%define develname %mklibname gearman -d

Summary:	Gearman Server and C Library
Name:		gearmand
Version:	0.22
Release:	%mkrel 1
License:	BSD
Group:		System/Servers
URL:		http://www.gearman.org/
Source0:	http://launchpad.net/gearmand/trunk/%{version}/+download/gearmand-%{version}.tar.gz
Source1:        gearmand.init
Source2:        gearmand.sysconfig
Source3:        gearmand.logrotate
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre):  rpm-helper
Requires(postun): rpm-helper
BuildRequires:	boost-devel
BuildRequires:	doxygen
BuildRequires:	e2fsprogs-devel
BuildRequires:	drizzle1-client-devel
BuildRequires:	libevent-devel
BuildRequires:	libmemcached-devel >= 0.42
BuildRequires:	libuuid-devel
BuildRequires:	memcached
BuildRequires:	tokyocabinet-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Gearman provides a generic framework to farm out work to other machines,
dispatching function calls to machines that are better suited to do work, to do
work in parallel, to load balance processing, or to call functions between
languages.

%package -n	%{libname}
Summary:	Shared Gearman Client Library
Group:		System/Libraries

%description -n	%{libname}
Gearman provides a generic framework to farm out work to other machines,
dispatching function calls to machines that are better suited to do work, to do
work in parallel, to load balance processing, or to call functions between
languages.

This package contains the Client Library.

%package -n	%{develname}
Summary:	Development files for the Gearman Server and C Library
Group:		Development/C
Requires:	%{libname} >= %{version}
Provides:	gearman-devel = %{version}

%description -n	%{develname}
Development files for the Gearman Server and C Library.

%prep

%setup -q

cp %{SOURCE1} gearmand.init
cp %{SOURCE2} gearmand.sysconfig
cp %{SOURCE3} gearmand.logrotate

%build
%serverbuild

%configure2_5x \
    --with-memcached=%{_sbindir}/memcached

%make

#%%check
#make check

%install
rm -rf %{buildroot}

%makeinstall_std

# don't fiddle with the initscript!
export DONT_GPRINTIFY=1

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}/var/log/%{name}
install -d %{buildroot}/var/run/%{name}

install -m0755 gearmand.init %{buildroot}%{_initrddir}/%{name}
install -m0644 gearmand.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -m0644 gearmand.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

touch %{buildroot}/var/log/%{name}/gearmand.log

%if %mdkversion < 200900
%post   -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%pre
%_pre_useradd %{name} /dev/null /bin/false

%postun
%_postun_userdel %{name}

%post
%create_ghostfile /var/log/%{name}/gearmand.log %{name} %{name} 0640
%_post_service %{name}

%preun
%_preun_service %{name}

%clean
rm -rf %{buildroot}

%files
%defattr(-, root, root)
%attr(0755,root,root) %{_initrddir}/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_bindir}/gearadmin
%{_bindir}/gearman
%{_sbindir}/gearmand
%{_mandir}/man1/gear*
%{_mandir}/man8/gear*
%attr(0711,%{name},%{name}) %dir /var/log/%{name}
%attr(0711,%{name},%{name}) %dir /var/run/%{name}
%ghost %attr(0640,%{name},%{name}) /var/log/%{name}/gearmand.log

%files -n %{libname}
%doc AUTHORS ChangeLog COPYING README
%defattr(-, root, root)
%{_libdir}/lib*.so.%{major}*

%files -n %{develname}
%defattr(-, root, root)
%dir %{_includedir}/libgearman
%{_includedir}/libgearman/*.h
%{_libdir}/lib*.*a
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/gearmand.pc
%{_mandir}/man3/gear*
