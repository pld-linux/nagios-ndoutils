# TODO
# - NDO2DB initscript (subpkg?)
# - add db/{installdb,upgradedb} (Perl) somewhere
%define		extraver	b7
%define		rel		0.1
Summary:	NDOUTILS (Nagios Data Output Utils) addon
Summary(pl.UTF-8):	Dodatek NDOUTILS (Nagios Data Output Utils)
Name:		nagios-ndoutils
Version:	1.4
Release:	0.%{extraver}.%{rel}
License:	GPL v2
Group:		Networking
Source0:	http://dl.sourceforge.net/nagios/ndoutils-%{version}%{extraver}.tar.gz
# Source0-md5:	a454f7434f401bd48047cc42b045ff8b
URL:		http://sourceforge.net/projects/nagios/
BuildRequires:	mysql-devel
Requires:	nagios >= 3.0
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
%setup -q -n ndoutils-%{version}%{extraver}

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir},%{_sysconfdir},%{_sbindir}}

install src/ndomod-3x.o $RPM_BUILD_ROOT%{_libdir}/ndomod.o
cp -a config/ndomod.cfg $RPM_BUILD_ROOT%{_sysconfdir}
echo 'broker_module=%{_libdir}/ndomod.o config_file=%{_sysconfdir}/ndomod.cfg' \
	> $RPM_BUILD_ROOT%{_sysconfdir}/ndomod-load.cfg

install src/ndo2db-3x $RPM_BUILD_ROOT%{_sbindir}/ndo2db
cp -a config/ndo2db.cfg $RPM_BUILD_ROOT%{_sysconfdir}

# daemon startup:
# ndo2db -c %{_sysconfdir}/ndo2db.cfg

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README REQUIREMENTS TODO UPGRADING
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ndo2db.cfg
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ndomod-load.cfg
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ndomod.cfg
%{_libdir}/ndomod.o
%attr(755,root,root) %{_sbindir}/ndo2db
