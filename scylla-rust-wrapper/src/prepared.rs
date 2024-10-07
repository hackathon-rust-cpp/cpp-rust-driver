use scylla::{frame::value::MaybeUnset::Unset, transport::PagingState};
use std::{os::raw::c_char, sync::Arc};

use crate::{
    argconv::*,
    cass_error::CassError,
    cass_types::{get_column_type, CassDataType},
    statement::{CassStatement, Statement},
    types::size_t,
};
use scylla::prepared_statement::PreparedStatement;

#[derive(Debug, Clone)]
pub struct CassPrepared {
    // Data types of columns from PreparedMetadata.
    pub variable_col_data_types: Vec<Arc<CassDataType>>,
    pub statement: PreparedStatement,
}

impl CassPrepared {
    pub fn new_from_prepared_statement(statement: PreparedStatement) -> Self {
        let variable_col_data_types = statement
            .get_variable_col_specs()
            .iter()
            .map(|col_spec| Arc::new(get_column_type(&col_spec.typ)))
            .collect();

        Self {
            variable_col_data_types,
            statement,
        }
    }
}

#[no_mangle]
pub unsafe extern "C" fn cass_prepared_free(prepared_raw: *const CassPrepared) {
    free_arced(prepared_raw);
}

#[no_mangle]
pub unsafe extern "C" fn cass_prepared_bind(
    prepared_raw: *const CassPrepared,
) -> *mut CassStatement {
    let prepared: Arc<_> = clone_arced(prepared_raw);
    let bound_values_size = prepared.statement.get_variable_col_specs().len();

    // cloning prepared statement's arc, because creating CassStatement should not invalidate
    // the CassPrepared argument
    let statement = Statement::Prepared(prepared);

    Box::into_raw(Box::new(CassStatement {
        statement,
        bound_values: vec![Unset; bound_values_size],
        paging_state: PagingState::start(),
        // Cpp driver disables paging by default.
        paging_enabled: false,
        request_timeout_ms: None,
        exec_profile: None,
    }))
}

#[no_mangle]
pub unsafe extern "C" fn cass_prepared_parameter_name(
    prepared_raw: *const CassPrepared,
    index: size_t,
    name: *mut *const c_char,
    name_length: *mut size_t,
) -> CassError {
    let prepared = ptr_to_ref(prepared_raw);

    match prepared
        .statement
        .get_variable_col_specs()
        .get(index as usize)
    {
        Some(col_spec) => {
            write_str_to_c(&col_spec.name, name, name_length);
            CassError::CASS_OK
        }
        None => CassError::CASS_ERROR_LIB_INDEX_OUT_OF_BOUNDS,
    }
}
