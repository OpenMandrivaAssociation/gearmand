%define major 6
%define libname %mklibname gearman %{major}
%define develname %mklibname gearman -d

Summary:	Gearman Server and C Library
Name:		gearmand
Version:	0.29
Release:	1
License:	BSD
Group:		System/Servers
URL:		http://www.gearman.org/
Source0:	http://launchpad.net/gearmand/trunk/%{version}/+download/gearmand-%{version}.tar.gz
Source1:        gearmand.init
Source2:        gearmand.sysconfig
Source3:        gearmand.logrotate
Patch0:		gearmand-0.28-drizzle_header_fix.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre):  rpm-helper
Requires(postun): rpm-helper
BuildRequires:	automake autoconf libtool
BuildRequires:	boost-devel
BuildRequires:	doxygen
BuildRequires:	drizzle1-client-devel
BuildRequires:	ext2fs-devel
BuildRequires:	hiredis-devel
BuildRequires:	libevent-devel
BuildRequires:	libmemcached-devel >= 1.0
BuildRequires:	libuuid-devel
BuildRequires:	lzmalib-devel
BuildRequires:	memcached >= 1.4.9
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig
BuildRequires:	postgresql-libs-devel >= 9.0
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
%patch0 -p0

cp %{SOURCE1} gearmand.init
cp %{SOURCE2} gearmand.sysconfig
cp %{SOURCE3} gearmand.logrotate

%build
%serverbuild

%configure2_5x \
    --enable-shared \
    --disable-static \
    --with-memcached=%{_bindir}/memcached \
    --with-memcached_sasl=%{_bindir}/memcached

# nuke rpath, fugly autopoo
perl -pi -e "s|^BOOST_LDPATH.*|BOOST_LDPATH=%{_libdir}|g" Makefile
perl -pi -e "s|^BOOST_PROGRAM_OPTIONS_LDFLAGS.*|BOOST_PROGRAM_OPTIONS_LDFLAGS=-L%{_libdir}|g" Makefile
perl -pi -e "s|^BOOST_PROGRAM_OPTIONS_LDPATH.*|BOOST_PROGRAM_OPTIONS_LDPATH=%{_libdir}|g" Makefile
perl -pi -e "s|^BOOST_THREAD_LDFLAGS.*|BOOST_THREAD_LDFLAGS=-L%{_libdir}|g" Makefile
perl -pi -e "s|^BOOST_THREAD_LDPATH.*|BOOST_THREAD_LDPATH=%{_libdir}|g" Makefile

%make

#%%check
#make check

%install
rm -rf %{buildroot}

# weird makefile poo
make DESTDIR=%{buildroot} install-exec-am install-data-am

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

# (oe) avoid pulling 32 bit libraries on 64 bit arch
%if "%{_lib}" == "lib64"
perl -pi -e "s|-L/usr/lib\b|-L%{_libdir}|g" %{buildroot}%{_libdir}/pkgconfig/*.pc
%endif

# cleanup
rm -f %{buildroot}%{_libdir}/*.*a

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
%dir %{_includedir}/libgearman-1.0
%{_includedir}/libgearman/*.h*
%{_includedir}/libgearman-1.0/*.h*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/gearmand.pc
%{_mandir}/man3/gear*
%{_mandir}/man3/libgearman.3*
