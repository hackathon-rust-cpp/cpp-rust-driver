%if 0%{!?amzn}
%define distnum %(/usr/lib/rpm/redhat/dist.sh --distnum)
%endif

Name:    scylla-cpp-driver
Epoch:   1
Version: %{driver_version}
Release: 1%{?dist}
Summary: C/C++ Driver for Scylla, Apache Cassandra and DataStax Products

Group: Development/Tools
License: Apache 2.0
URL: https://github.com/scylladb/cpp-driver
Source0: %{name}-%{version}.tar.gz
Source1: scylla-cpp-driver.pc.in
Source2: scylla-cpp-driver_static.pc.in

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%if 0%{?distnum} >= 8
%define cmakecmd cmake
BuildRequires: cmake >= 3.5.0
%else
BuildRequires: cmake3 >= 3.5.0
%define cmakecmd cmake3
%endif

BuildRequires: libuv-devel >= %{libuv_version}
BuildRequires: openssl-devel >= 0.9.8e
Provides: libscylla-cpp-driver.so()(64bit)

%description
A modern, feature-rich, shard-aware, and highly tunable C/C++ client library for 
ScyllaDB, Apache Cassandra and DataStax Products using Cassandra's native protocol and
Cassandra Query Language along with extensions for DataStax Products.

%package devel
Summary: Development libraries for ${name}
Group: Development/Tools
Requires: %{name} = %{epoch}:%{version}-%{release}
Requires: libuv >= %{libuv_version}
Requires: openssl >= 0.9.8e
Requires: krb5-libs
Requires: pkgconfig

%description devel
Development libraries for %{name}

%global debug_package %{nil}

%prep
%setup -qn %{name}-%{version}

%build
export CFLAGS='%{optflags}'
export CXXFLAGS='%{optflags}'
%{cmakecmd} -DCMAKE_BUILD_TYPE=RELEASE -DCASS_BUILD_STATIC=ON -DCASS_INSTALL_PKG_CONFIG=OFF -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} -DCMAKE_INSTALL_LIBDIR=%{_libdir} .
make %{?_smp_mflags}
cp ../../../*.so libscylla-cpp-driver.so.2.16.2
ln -s libscylla-cpp-driver.so libcassandra.so
ln -s libscylla-cpp-driver_static.a libcassandra_static.a

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

mkdir -p %{buildroot}/%{_libdir}/pkgconfig
sed -e "s#@prefix@#%{_prefix}#g" \
    -e "s#@exec_prefix@#%{_exec_prefix}#g" \
    -e "s#@libdir@#%{_libdir}#g" \
    -e "s#@includedir@#%{_includedir}#g" \
    -e "s#@version@#%{version}#g" \
    %SOURCE1 > %{buildroot}/%{_libdir}/pkgconfig/scylla-cpp-driver.pc
sed -e "s#@prefix@#%{_prefix}#g" \
    -e "s#@exec_prefix@#%{_exec_prefix}#g" \
    -e "s#@libdir@#%{_libdir}#g" \
    -e "s#@includedir@#%{_includedir}#g" \
    -e "s#@version@#%{version}#g" \
    %SOURCE2 > %{buildroot}/%{_libdir}/pkgconfig/scylla-cpp-driver_static.pc

%clean
rm -rf %{buildroot}

%check
# make check

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc README.md LICENSE.txt
%{_libdir}/*.so
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root)
%doc README.md LICENSE.txt
%{_includedir}/*.h
%{_libdir}/*.a
%{_libdir}/pkgconfig/*.pc

%changelog
* Mon Mar 13 2017 Michael Penick <michael.penick@datastax.com> - 2.6.0-1
- release
