encoding.process_tokens_with_offsets_mut(|(i, (token, offsets))| {
    // offsets を実際に変更しない・書き込まないなら mut を削除
    // ...
}); 