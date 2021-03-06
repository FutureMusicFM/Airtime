use utf8;
package Airtime::Schema::Result::CcPlaylist;

# Created by DBIx::Class::Schema::Loader
# DO NOT MODIFY THE FIRST PART OF THIS FILE

=head1 NAME

Airtime::Schema::Result::CcPlaylist

=cut

use strict;
use warnings;

use Moose;
use MooseX::NonMoose;
use MooseX::MarkAsMethods autoclean => 1;
extends 'DBIx::Class::Core';

=head1 COMPONENTS LOADED

=over 4

=item * L<DBIx::Class::InflateColumn::DateTime>

=back

=cut

__PACKAGE__->load_components("InflateColumn::DateTime");

=head1 TABLE: C<cc_playlist>

=cut

__PACKAGE__->table("cc_playlist");

=head1 ACCESSORS

=head2 id

  data_type: 'integer'
  is_auto_increment: 1
  is_nullable: 0
  sequence: 'cc_playlist_id_seq'

=head2 name

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 0
  size: 255

=head2 mtime

  data_type: 'timestamp'
  is_nullable: 1

=head2 utime

  data_type: 'timestamp'
  is_nullable: 1

=head2 creator_id

  data_type: 'integer'
  is_foreign_key: 1
  is_nullable: 1

=head2 description

  data_type: 'varchar'
  is_nullable: 1
  size: 512

=head2 length

  data_type: 'interval'
  default_value: '00:00:00'
  is_nullable: 1

=cut

__PACKAGE__->add_columns(
  "id",
  {
    data_type         => "integer",
    is_auto_increment => 1,
    is_nullable       => 0,
    sequence          => "cc_playlist_id_seq",
  },
  "name",
  { data_type => "varchar", default_value => "", is_nullable => 0, size => 255 },
  "mtime",
  { data_type => "timestamp", is_nullable => 1 },
  "utime",
  { data_type => "timestamp", is_nullable => 1 },
  "creator_id",
  { data_type => "integer", is_foreign_key => 1, is_nullable => 1 },
  "description",
  { data_type => "varchar", is_nullable => 1, size => 512 },
  "length",
  { data_type => "interval", default_value => "00:00:00", is_nullable => 1 },
);

=head1 PRIMARY KEY

=over 4

=item * L</id>

=back

=cut

__PACKAGE__->set_primary_key("id");

=head1 RELATIONS

=head2 cc_playlistcontents

Type: has_many

Related object: L<Airtime::Schema::Result::CcPlaylistcontent>

=cut

__PACKAGE__->has_many(
  "cc_playlistcontents",
  "Airtime::Schema::Result::CcPlaylistcontent",
  { "foreign.playlist_id" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 creator

Type: belongs_to

Related object: L<Airtime::Schema::Result::CcSubj>

=cut

__PACKAGE__->belongs_to(
  "creator",
  "Airtime::Schema::Result::CcSubj",
  { id => "creator_id" },
  {
    is_deferrable => 0,
    join_type     => "LEFT",
    on_delete     => "CASCADE",
    on_update     => "NO ACTION",
  },
);


# Created by DBIx::Class::Schema::Loader v0.07038 @ 2013-12-30 17:33:31
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:gssrCT4IK3qlj/SYXtBWdA


# You can replace this text with custom code or comments, and it will be preserved on regeneration
__PACKAGE__->meta->make_immutable;
1;
