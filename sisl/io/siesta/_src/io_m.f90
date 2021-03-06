!> Module for handling free units and checking whether stuff succeeded
module io_m

  implicit none

  public :: open_file
  public :: iostat_reset
  public :: iostat_update
  public :: iostat_query

  integer, private :: io_stat = 0

contains

  !< Open the file `file` using the given `action`, `status` and `form` specifications.
  subroutine open_file(file, action, status, form, unit)
    character(len=*), intent(in) :: file
    character(len=*), intent(in) :: action, status, form
    integer, intent(out) :: unit

    logical :: opened
    integer :: ierr

    ! Check out whether the file is already opened and
    ! if we can reuse it...
    unit = -1
    inquire(file=file, number=unit, opened=opened, iostat=ierr)
    call iostat_update(ierr)

    if ( unit > 0 ) then

      ! The file is already open
      ! Depending on the action, we need to rewind or close it
      select case ( action )
      case ( 'r', 'R', 'read', 'READ' )

        ! It is already opened, simply rewind and return...
        rewind(unit)
        return

      case ( 'w', 'W', 'write', 'WRITE' )

        close(unit)

      end select

    end if

    ! Always reset
    call iostat_reset()

    ! We need to open it a-new
    unit = 999
    opened = .true.
    do while ( opened )

      unit = unit + 1
      inquire(unit, opened=opened)

    end do

    open(unit, file=trim(file), status=status, form=form, action=action, iostat=ierr)
    call iostat_update(ierr)

  end subroutine open_file

  !< Initialize global io stat
  subroutine iostat_reset()
    io_stat = 0
  end subroutine iostat_reset

  !< Update global status, only overwrite if not used
  subroutine iostat_update(iostat)
    integer, intent(in) :: iostat

    ! Define f2py intents
!f2py intent(out)  :: iostat

    if ( io_stat == 0 ) io_stat = iostat

  end subroutine iostat_update

  !< Query the status of io
  subroutine iostat_query(iostat)
    integer, intent(out) :: iostat

    ! Define f2py intents
!f2py intent(out)  :: iostat

    iostat = io_stat

  end subroutine iostat_query

end module io_m
