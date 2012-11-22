# TODO
# - add db/{installdb,upgradedb} (Perl) somewhere
# - ndo2db is unable to start, if there's stale socket:
#   srwxr-xr-x 1 nagios nagios 0 Jan 15  2012 /var/lib/nagios/ndo.sock=
#
# Conditional build:
%bcond_with	pgsql	# build without pgsql support (does not seem to work)
%bcond_without	mysql	# build without mysql support
%bcond_without	ssl	# build without ssl support

%define		addon	ndoutils
Summary:	NDOUTILS (Nagios Data Output Utils) addon
Summary(pl.UTF-8):	Dodatek NDOUTILS (Nagios Data Output Utils)
Name:		nagios-%{addon}
Version:	1.5.2
Release:	1
License:	GPL v2
Group:		Networking
Source0:	http://downloads.sourceforge.net/nagios/%{addon}-%{version}.tar.gz
# Source0-md5:	61460320d0deb8109e7e45e2b717ce1f
Source1:	ndo2db.init
Patch0:		config.patch
URL:		http://sourceforge.net/projects/nagios/
%{?with_mysql:BuildRequires:	mysql-devel}
%{?with_ssl:BuildRequires:	openssl-devel}
%{?with_pgsql:BuildRequires:	postgresql-devel}
BuildRequires:	rpmbuild(macros) >= 1.228
Requires:	nagios >= 3.0
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios
%define		_libdir		%{_prefix}/%{_lib}/nagios

%description
The NDOUTILS (Nagios Data Output Utils) addon allows you to move
status and event information from Nagios to a database for later
retrieval and processing.

%description -l pl.UTF-8
Dodatek NDOUTILS (Nagios Data Output Utils) pozwala przenosić
informacje o stanie i zdarzeniach z Nagiosa do bazy danych w celu
późniejszego odczytu i przetwarzania.

%prep
%setup -q -n %{addon}-%{version}
%patch0 -p1

# some typo ;)
grep -r 20052-2009 -l . | xargs sed -i -e 's,20052-2009,2005-2009,'

%build
%configure \
	--bindir=%{_sbindir} \
	--localstatedir=/var/lib/nagios \
	--with-init-dir=/etc/rc.d/init.d \
	%{?with_mysql:--enable-mysql} \
	%{?with_pgsql:--enable-pgsql} \
	%{?with_ssl:--enable-ssl} \
	--enable-nanosleep \
	%{nil}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir},%{_sysconfdir},%{_sbindir}}

%{__make} fullinstall \
	INSTALL_OPTS="" \
	INIT_OPTS="" \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ndo2db

mv $RPM_BUILD_ROOT{%{_sbindir},%{_libdir}}/ndomod.o

for sample in $RPM_BUILD_ROOT%{_sysconfdir}/*-sample; do
	cfg=${sample%%-sample}
	mv $sample $cfg
done

# sample line that should be added to nagios.cfg for this module to work
echo 'broker_module=%{_libdir}/ndomod.o config_file=%{_sysconfdir}/ndomod.cfg' \
	> $RPM_BUILD_ROOT%{_sysconfdir}/ndomod-load.cfg

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add ndo2db
%service ndo2db restart

%preun
if [ "$1" = "0" ]; then
	%service -q ndo2db stop
	/sbin/chkconfig --del ndo2db
fi

%files
%defattr(644,root,root,755)
%doc README REQUIREMENTS TODO UPGRADING db
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ndo2db.cfg
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ndomod-load.cfg
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ndomod.cfg
%attr(754,root,root) /etc/rc.d/init.d/ndo2db
%attr(755,root,root) %{_sbindir}/file2sock
%attr(755,root,root) %{_sbindir}/log2ndo
%attr(755,root,root) %{_sbindir}/ndo2db
%attr(755,root,root) %{_sbindir}/sockdebug

%attr(755,root,root) %{_libdir}/ndomod.o
